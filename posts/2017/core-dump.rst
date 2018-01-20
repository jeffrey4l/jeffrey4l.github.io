Core Dump
#########

:date: 2017-12-04
:tags: Linux, Docker
:slug: core-dump
:category: Linux


容器化后，容器里面的进程如果出现 core dump ，默认情况下，dump 出来的文件是存放在容器内部的根目录的。这样会导致以下几个问题

1. 如果 Docker 使用的 LVM 的驱动，每个容器默认大小只有 10G, 很容易占用了全部的容器空间，而导致容器不能启动。
2. Core Dump 文件存到容器中，也很容易被删除掉，从而不容易排查问题。

想要解决这个问题，就要先了解什么是 Core Dump。

0x01 - core dump
================

Core dump 功能能够把进程出问题的时候的信息保存下来，方便我们来调试。触发方法，可以通过给某个进程发送:code:`SIGSEGV` 信号

::

    kill -SIGSEGV <pid>
    ls core.<pid>

dump 出来的文件可以通过 :code:`gdb` 来查看内容，基本使用方法如下：


:: 

    gdb /path/to/binary /path/to/core.dump.file

* :code:`bt` commands to get the information.
* :code:`bt full` commands to get the detailed backtrace
* :code:`info locals` to see all the local variables.
* :code:`print variable-name` to print the variables
* :code:`frame frame-number` to go to desired frame number.
* :code:`up n` and :code:`down n` commands to select frame n frames up and select frame n frames down respectively.

默认情况下，生成的转存文件保存在当前目录下面，并且每个文件很大。从而占用大量空间。 通过 ulimit 可以控制，但是需要注意的是这种方法只能控制 单个core 文件的大小，并不能控制总 core dump 文件的大小或个数，而且也有可能生成不完整的 core dump 文件。
方法如下：

::

    // 单位是 KB, 0 意味着关闭
    ulimit -c 0
    // or
    ulimit -c 100
    // or
    ulimit -c ulimited

0x02 - 容器化
=============

容器里面，ulimit 是由 systemd 及 docker 共同控制的。
systemd 的 docker.service 可以控制 dockerd 进程的上限

::

    [Service]
    LimitNOFILE=1048576
    LimitNPROC=infinity
    LimitCORE=infinity

与此同时， docker 也可以控制单个容器的 ulimit 大小

::

    docker run --ulimit core=1024000 centos:7

或在 dockerd 启动的时候，设置所有容器的默认的 ulimit 大小

:: 

    dockerd --ulimit core=1024000

但是，容器内的进程core dump的时候，还是保存到了容器内部，会严重影响docker的运行。然后完全关掉 core dump 功能也不是一个好办法。这个时候就需要借助 systemd 来转存。

0x03 - Systemd
==============

现在主流的操作系统都已经转到了 systemd, 所在这个办法适用于大部分操作系统。

自从 linux 2.6.19，支持通过 :code:`/proc/sys/kernel/core_pattern` 来配置转存的 core dump, 方法如下：

::

    $ cat << EOF >>  /etc/sysctl.conf
    kernel.core_pattern = |/usr/lib/systemd/systemd-coredump %P %u %g %s %t %c %e
    EOF

这个是配置到宿主机的内核上，因为容器共用宿主机的内核，所以当容器里面的进程需要 core dump 时，会转存到宿主机上的 systemd。而且systemd在保存的时候，经过了压缩，还可以控制存储空间的总大小，从而避免core dump吃掉太多硬盘空间。具体参看 :code:`/etc/systemd/coredump.conf`

0x04 - coredumpctl
==================

转存到宿主机上，可以通过 coredumpctl 来进程查看，基本操作如下。

::

    coredumpctl list
    coredumpctl dump <match>
    coredumpctl info <match>
    coredumpctl gdb <match>

使用这种方法，可以避免 Core Dump 占用容器空间有问题，同时还可以保存转存的文件，方便之后的调试查看。

0x05 - REF
==========

* https://lwn.net/Articles/280959/
* http://man7.org/linux/man-pages/man5/core.5.html
* https://wiki.archlinux.org/index.php/Core_dump
