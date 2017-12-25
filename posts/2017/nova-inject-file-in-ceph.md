title: 使用nova支持向rbd盘中注入文件
date: 2017-12-25
slug: nova-inject-file-in-ceph

## 引子

很多 OpenStack 与 Ceph 部署集成的文档都会告诉你，libivrt 的文件和密码注入是在 Ceph 上面是不支持的。需要使用下面的配置文件关闭。

    ::ini
    [libvirt]
    inject_password = false
    inject_key = false
    inject_partition = -2

但是真的只是不支持这么简单么? 首先看 nova 的注入是如何工作的。

## nova 是怎么注入的文件的

nova 使用 libguestfs 来文件密码的注入

libguestfs主要有三个大的部分：`guestfsd`, `guestfs-lib` ,`guestfish`。

**guestfsd是一个daemon**，但是它不是运行在 host 上的 daemon，它运行在 guest 上，libguestfs 首先用`febootstrap`和`febootstrap-supermin-helper`两个工具将 host 中的 kernel，用得到的一些 modules，配置文件和一些工具重新组合到一起，接着在后台启动一个 qemu 进程启动这个由`febootstrap`生成的 image。在用 qemu 启动的这个 guest 里运行`guestfsd`。`guestfsd`通过 socket 和 host 进行通信，之间建立了一个通信的协议，它可以通过 socket 接受来自host端`guestfs-lib`写到 socket 的数据。guestfsd 通过分析接受到的数据，进而执行相应的操作。

**guestfs-lib是一个库**，它实现了一些 libguestfs 的库函数 `guestfs_*`。这些库函数向 socket 发送相应的数据，数据就会被 guest 端的 guestfsd 接收到，进而分析所要执行的操作。 

**guestfish是对 guestfs-lib 接口函数的一些应用**，guestfish 的命令都是通过调用`guestfs-lib`的库函数来实现的。

如果在 nova 中开启了 inject 功能，nova 会调用 libguestfs 的接口，把文件或密码注入到镜像中去，然后再去真正的启动用户的虚拟机。那支持 ceph 里面的镜像么?

## libguestfs 对 rbd 的支持

libguestfs 对 rbd 的支持是从 1.21.21 这个版本开始的[^1]，并且测试并不充分[^2], 这个版本也是13年5月份才发布的。到现在 CentOS6 上面的 libguestfs 版本还是 1.20.11。所以早期时候，文档中建议关掉 inject 功能，是确实 libguestfs 不支持RBD上面的镜像。

但是 CentOS7 上面，libguestfs 已经支持这个功能，所以是可以打开 nova 的注入功能的。那我们是不是就可以把这个功能打开了?

## libvirt 注入的问题

**不支持 Boot from volume**[^3], 当从 Volume 启动的时候，并不支持文件注入。

**社区也准备废弃这个功能**，有几个原因。1是代码层面上，如果注入失败了，没有任何错误信息报出来。2是文件注入并不安全。3是这些注入的文件并没有持久化(存入数据库)，在 `evacuate` 或 `unshelve` 的时候，这些文件会被丢掉。 4是可以通过 metadata-api 或 config-drive 更方便的实现文件注入功能。有兴趣可以读下相关信息[^4][^5][^6][^7]

## 结论

通过 libvirt 注入的方式并不被社区推荐，应该采用 metadata-api 或 config drive 方式才是更加可取。

[^1]: <https://github.com/libguestfs/libguestfs/commit/694a091d3faac78acbd0b5a368856b569c7ba5e2>
[^2]: <https://github.com/libguestfs/libguestfs/commit/186bb67c6e8496d04a6f5646df9b2fb483cdc189>
[^3]: <https://github.com/openstack/nova/blob/master/nova/virt/libvirt/driver.py#L3269>
[^4]: <http://lists.openstack.org/pipermail/openstack-dev/2016-November/107195.html>
[^5]: <http://lists.openstack.org/pipermail/openstack-dev/2016-July/098703.html>
[^6]: <http://lists.openstack.org/pipermail/openstack-dev/2017-March/113171.html>
[^7]: <https://review.openstack.org/509013>
