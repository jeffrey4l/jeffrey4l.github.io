Title: iptables forward the vrrp packets issue
Date: 2016-2-2
Slug: iptables-forward-the-vrrp-packets-issue
Category: Linux
Tags: iptables, vrrp

![功夫熊猫](images/kungfupanda.jpg)

最近在整 Kolla 的多机部署，没有物理环境还是在虚拟机上搞。不过今天被一个 keepalived 的问题卡了将近一天的时间。倒也不是啥大问题，还是栽到了自己挖的坑里。

## 问题

先说一下自己的环境，我使用了三台 kvm 虚拟机，每台两张网卡，一个用于上外网(eth0 `10.2.0.0/24`)，一个用于 neutron 的 tenant 网络使用(eth1)。问题就出在 eth0 上面。eth0 是桥在了我手动创建的一个桥上 (br0), 为了上外网，我打开了 `ip_forward`， 并加了一条 iptables 转发规则：

```
iptables -t nat -A POSTROUTING -s 10.2.0.0/24 ! -d 10.2.0.0/24 -j MASQUERAE
```

一般情况下是没有问题的，但是加了 `keepalived` 就完了。vip 跑到了所有的机器上，感觉就是没有通讯上，或是选举有问题。重新核对了半天配置没有发现问题。由于 Kolla 里是用 docker 跑的 keepalived ，为了排除是 Docker 本身有问题，我还在虚拟机的系统上部署了 keepalived 的，还是同样的问题。

## 原因

最后在一次偶然的抓包中发现，所有机器上抓到的 vrrp 的包源地址居然都是网关(`10.2.0.1`)发出来的，这还能不出问题? 

查了查 vrrp 包，原来是在四层协议上，和 tcp/udp 是并列的。再看一眼自己的 iptables ， 就知道是怎么回事了。后来把 iptables 改的明确了一些, 只 SNAT tcp,udp及icmp的协议，问题终于解决了。

```
-A POSTROUTING -s 10.2.0.0/24 ! -d 10.2.0.0/24 -p tcp -j MASQUERADE
-A POSTROUTING -s 10.2.0.0/24 ! -d 10.2.0.0/24 -p udp -j MASQUERADE
-A POSTROUTING -s 10.2.0.0/24 ! -d 10.2.0.0/24 -p icmp -j MASQUERADE
```

## 教训

* tcpdump 还是很有用的东西
* 四层上的协议除了 tcp/udp 还是有很多的 [^1]

## REF

[^1]: <https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers>
