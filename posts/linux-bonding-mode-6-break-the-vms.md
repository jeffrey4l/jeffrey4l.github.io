---
title: linux bonding mode 6 break the vms
date: 2014-04-14 19:39:51
tags: Network
Category: Linux
---

操作系统： ubuntu 12.04.1
内核 linux 3.2

今天发现一个网络上的问题，如果 Openstack Fixed IP 走 mode 6 绑定的网卡，不同物理机上的虚拟机是相互访问不了的。

```text
    +---- host1 -------+         +---- host2 ----+
                     eth0 ---- eth0 
                   /                \
    br1 ---- bond0                   bond0 ---- br1 
                   \                /
                     eth0 ---- eth0 
```


机器的连接方式如上图，经检查发现，问题简化成两边的 br1 是不通的，现像是ping时，接收方收不到包，包只走到bond0就给丢弃了。原因在于内核上有问题。在网络上查到以下两个连接 

1. <https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1098302>
2. <https://bugzilla.redhat.com/show_bug.cgi?id=487763>

把内核升级到3.8之后就可以了。

    apt-get install linux-image-generic-lts-raring
