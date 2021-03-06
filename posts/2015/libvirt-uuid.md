Title: 修改 Libvirt 的 UUID
Date: 2015-2-10
Tags: Libvirt
Category: Linux
Slug: libvirt-uuid

由于物理机器有限，想做OpenStack的多机环境一直是个问题。之前是在OpenStack上部署OpenStack。由于只有一台物理机，资源相当紧张。不能建太多机器。最近突然想，既然 LXC 现在已经很完善了。能不能就利用它来做 OpenStack 服务间的隔离呢。所以最近一直在搞这东西。搞了几天还是有效果的。基本搭建了 OpenStack + Ceph + Swift 的环境出来。其中网络用的 Neutron + ML2 + OVS + VLAN。由于用 LXC 的隔离的，相对于之前来说相当节省资源。很好的解决了资源的问题。可以做一些大量机器的实验了。之后也会也这其中遇到的一些问题写下来，备忘。

今天主要写下配置 Live Migration 过程中遇到的一个问题。

每个 Libvirtd 实例都会有一个 UUID 存在。不同的 libvirt 实例的 UUID 应该是不同的。否则在 migrate 过程中， libvirt 会认为自己是在向自己迁移从而导致迁移失败。这个UUID有一个默认值，是来自于 SMBIOS UUID。这两个UUID可以通过以下方法拿到：

```
$ dmidecode  -s system-uuid
4C4C4544-0032-3210-804C-C7C04F463358

$ virsh capabilities | grep uuid
<uuid>44454c4c-3200-1032-804c-c7c04f463358</uuid>
```

可以看到这两个值是一样的(不知道为什么有一段顺序不对)。

当我在不同的 LXC 中启动多个 libvirt 时，就会触发这个问题。所有的 libvirt 使用的是相同的 uuid 从而导致 live migration 失败。

修改的办法也很简单。这个UUID可以在 libvirt 的配置文件`/etc/libvirt/libvirtd.conf`中修改后重启libivrt就可以了。

```
host_uuid = "8ba976e9-1224-4339-9526-719fe6dee311"
```

# REF

* [Libvirt Capability Information](http://libvirt.org/guide/html/Application_Development_Guide-Connections-Capability_Info.html)
