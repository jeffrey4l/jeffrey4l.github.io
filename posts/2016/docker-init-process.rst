Docker init 进程
================

:date: 2016-11-07
:tag: Linux, Docker
:slug: docker-init-process

应用容器化后，重启容器的时候，经常会很慢，而且docker daemon 日志中经常会抛出以
下错误

::

    dockerd[559]: msg="Container 5054f failed to exit within 10 seconds of
    signal 15 - using the force"

默认的的 signal 15 根本就没有使其退出，最后还是 10 秒超时后强制退出(kill)的。而
且有时还会出现大量僵尸进程

这可不是一个好现象。本文解释其原因及解决方法。

背景知识
--------

信号
~~~~

这个是 Linux 最常见一个概念，一般杀死进程时都会用到 ``kill <pid>`` 。 不同的信
号有不同的默认行为。用户可以注册自己的信号处理函数，来覆盖掉默认行为。

僵尸进程
~~~~~~~~

僵尸进程是终止运行的进程，为什么它们是有害的? 

虽然应用申请的内存已经释放了，但是你依然能通过 ``ps`` 看到它。这是因为有一些内
核资源没有释放。下面是 Linux ``waitpid`` 的 man page:

    As long as a zombie is not removed from the system via a wait, it will
    consume a slot in the kernel process table, and if this table fills, it
    will not be possible to create further processes."


容器化后的问题
--------------

容器化后，由于单容器单进程，已经没有传统意义上的 init 进程了。应用进程直接占用
了 pid 1 的进程号。从而导致以下两个问题。

进程不能正常终止
~~~~~~~~~~~~~~~~

Linux 内核中会对 pid 1 进程发送特殊的信号量。

一般情况下，当给一个进程发送信号时，内核会先检查是否有用户定义的处理函数，如果
没有，就会回退到默认行为。例如使用 SIGTERM 直接杀死进程。然而，如果进程的 PID
是 1, 内核会特殊对待它。如果没有没有注册用户处理函数，内核不会回退到默认行为，
什么也不做。换句话说，如果你的进程没有处理信号的函数，给他发送 ``SIGTERM`` 会一
点效果也没有。

常见的使用是 docker run my-container script. 给 ``docker run`` 进程发送
``SIGTERM`` 信号会杀掉 ``docker run`` 进程，但是容器还在后台运行。

孤儿僵尸进程不能正常回收
~~~~~~~~~~~~~~~~~~~~~~~~

当进程退出时，它会变成僵尸进程，直到它的父进程调用 ``wait()`` ( 或其变种 ) 的系
统调用。process table 里面会把它的标记为 ``defunct`` 状态。一般情况下，父进程应
该立即调用 ``wait()``, 以防僵尸进程时间过长。

如果父进程在子进程之前退出，子进程会变成孤儿进程, 它的父进程会变成 PID 1。因此
，init 进程就要对这些进程负责，并在适当的时候调用 ``wait()`` 方法。

但是，通常情况下，大部分进程不会处理偶然依附在自己进程上的随机子进程，所以在容器
中，会出现许多僵尸进程。
    
解决方案
--------

让所有的应用能正确的处理以上的情况，不太现实。好在现在有很多解决方案，例如
dumb-init [0] 。他像是一个小型 init 服务，他启动一个子进程并转发所有接收到的信
号量给子进程。而且不需要修改应用代码。

此时你的应用进程已经不是 pid 1 了，所以已经没有上面提到的问题。而且 dumb-init
也会转发所有的信号给子进程，应用的形为和在没有 dumb-init 时是一样的。如果应用进
程死掉了，dumb-init 进程也会死掉，并会清理所有其它的子进程。

使用方法如下, 在 Dockerfile 里面加上：

::

    # install dumb-init
    RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64
    RUN chmod +x /usr/local/bin/dumb-init

    # Runs "/usr/bin/dumb-init -- /my/script --with --args"
    ENTRYPOINT ["/usr/bin/dumb-init", "--"]
    CMD ["/my/script", "--with", "--args"]

类似的方案 tini [1], pidunu[3]

Kolla 相关
----------

Kolla 最近已经发布了 newton 版本的 release 。 已经加上了 dumb-init 的解决方案。


参考资料
--------
[0] https://github.com/Yelp/dumb-init
[1] https://github.com/krallin/tini
[2] https://blog.phusion.nl/2015/01/20/docker-and-the-pid-1-zombie-reaping-problem
[3] https://github.com/rciorba/pidunu
