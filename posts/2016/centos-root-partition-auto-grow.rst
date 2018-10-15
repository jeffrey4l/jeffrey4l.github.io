CentOS 根分区自动扩展
=====================

:date: 2016-11-14
:slug: centos-root-partition-auto-grow
:category: Linux
:tags: Linux, OpenStack

CentOS 5 太老了，完全不支持。

CentOS 6 要实现分区自动扩展，要安装以下三个包

::

    yum -y install cloud-init cloud-utils-growpart dracut-modules-growroot
    # 生新生成 initramfs
    dracut -f
    systemctl enable cloud-init

``dracut`` 把 ``growroot`` 的脚本封装到 ``initramfs`` 里面。 把系统启动时，
``initramfs`` 利用 ``growpart`` 命令把根分区进行扩展。然后启动真正的
``kernel``, 之后 ``cloud-init`` 服务会自动把文件系统进行扩展。

之所以使用 ``initramfs`` 这种方式，原因[0]：

    Growpart called by cloud-init only works for kernels >3.8. Only newer
    kernels support changing the partition size of a mounted partition. When
    using an older kernel the resizing of the root partition happens in the
    initrd stage before the root partition is mounted and the subsequent
    cloud-init growpart run is a no-op.

CentOS 7 使用的是 3.10 ( > 3.8 ) 的内核，所以并不需要 dracut-modules-growroot
包( 源里面也并没有这个包 )。 只安装以下两个包就可以了。

::

    yum -y install cloud-init cloud-utils-growpart
    systemctl enable cloud-init

* [0] http://openstack.openstack.narkive.com/opyLuPqC/centos-6-5-cloud-init-growpart-resizefs-does-not-work-on-first-boot

