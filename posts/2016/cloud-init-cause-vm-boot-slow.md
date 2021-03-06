Title: cloud-init 导致虚拟机启动太慢
Date: 2016-04-10
Slug: cloud-init-cause-vm-boot-slow
Category: OpenStack
Tags: OpenStack

[TOC]

## 问题

在一个准生产环境中，一直发现虚拟机启动太慢的问题，现像是虚拟机很早就能 ping 到，但是就是 ssh 不进去。要么报端口没有开启，要么就 Public Key 不对。整个过程大概要2分多钟才能直接 ssh 进去。

## 背景知识

cloud-init 这个服务是从 AWS 学来的。它安装在虚拟机中，在启动虚拟机时，做一些初始化工作。如：硬盘分区自动扩展，SSH Public Key 注入，用户创建等。用户甚至可以注入一些 shell 脚本到虚拟机中运行。在自动化方便启了很大的作用。Heat 的实现就依赖于 cloud-init 服务。

在 OpenStack 上，cloud-init 应该从 `http://169.254.169.254` 去拿到所需要的信息。而这个服务是通过 iptables 转到了 neutron-metadata-agent 服务上

## 环境

使用 Kolla 安装的 OpenStack Mitaka 版本的多机环境，镜像使用的是 CentOS 7 和 Ubuntu 14.04, 均是从官方下载的。由于一些安全限制，虚拟机不能访问外网。

## 调试

测试虚拟机用的 CentOS 7 系统，

首先看虚拟机的 console log, 发现如下信息

```
Starting kdump:[  OK  ]
Starting cloud-init: Cloud-init v. 0.7.5 running 'init' at Wed, 30 Mar 2016 14:58:36 +0000. Up 40.68 seconds.
...
Starting cloud-init: Cloud-init v. 0.7.5 running 'modules:config' at Wed, 30 Mar 2016 14:59:59 +0000. Up 124.27 seconds.
Starting cloud-init: Cloud-init v. 0.7.5 running 'modules:final' at Wed, 30 Mar 2016 15:00:01 +0000. Up 126.22 seconds.
...
Cloud-init v. 0.7.5 finished at Wed, 30 Mar 2016 15:00:01 +0000. Datasource DataSourceOpenStack [net,ver=2].  Up 126.41 seconds
```

发现: cloud-init 服务从开始启动到最后完成，花了 80 多秒，大部分的时间都是花在了 init 环节上。按说是不应该的。

一开始我怀疑是硬盘分区自动扩展慢导致的，但把自动扩展关掉了也还是一样，时间基本没有变化。肯定是其它问题。

万事找日志，要找真正的原因，还是从日志找起。

在 `/var/log/` 下找日志，只发现了少量日志。大概看了一个 cloud-init 的源代码，日志应该会有很多的才对。

    ::console
    -rw-r--r--. 1 root root    0 Mar 30 14:58 cloud-init.log
    -rw-r--r--. 1 root root 1.7K Mar 30 15:00 cloud-init-output.log

又尝试修改了 `cloud.cfg` 的配置，把日志都都打印到特定文件，如下。但是结果还是一样，没有啥新日志信息。(其时后来才发现，这个配置默认就存在，在 `/etc/cloud/cloud.cfg.d/` 下面)

    ::yaml
    output: {all: '| tee -a /var/log/cloud-init-output.log'}

联想到 CentOS 7 用的 systemd 管理器，试图从 systemd 里找日志。先找到了所有的 cloud-init 相关的服务

    ::console
    $ systemctl list-units | grep cloud
    cloud-config.service       Apply the settings specified in cloud-config
    cloud-final.service        Execute cloud user/final scripts
    cloud-init-local.service   Initial cloud-init job (pre-networking)
    cloud-init.service         Initial cloud-init job (metadata service crawler)
    cloud-config.target        Cloud-config availability

可以看到，cloud-init 安装的服务还是有多个的。不同的服务的启动时间点和所做的事情是不一样的。使用 `journalctl` 挨个排查后，找到以下日志：

    ::console
    $ journalctl -u cloud-init
    ...
    Apr 03 13:19:33 cloud-init[780]: [CLOUDINIT] __init__.py[DEBUG]: Merging using located merger
    Apr 03 13:21:13 cloud-init[780]: [CLOUDINIT] DataSourceGCE.py[DEBUG]: http://metadata.google.internal./computeMetadata/v1/ is not resolvable
    ...

注意前面的时间点，这两行日志间差了60多秒，而且后面是一个错误，明显是在等一个超时，时间是花在这的。至此原因找到了。

## 原因分析

cloud-init 是一个通用程序，能兼容多个云环境。他会从多个数据源里去读 Metadata 数据。其默认的顺序中，GoogleGCE 在 OpenStack 之前，而 GoogleGCE 的源里面，会访问一个 http://metadata.google.internal. 的网址，加上虚拟机不能访问外网，程序会卡在这里，直到超时。才会继续测试 OpenStack 的源是否可用。

## 解决方法

尽量不要直接使用官方的源，而是自己制作，尤其是 cloud-init 的配置项。要手动修改掉其默认的数据源，以避免以上情况的发生。


    ::yaml
    # /etc/cloud/cloud.cfg
    datasource_list: ['ConfigDrive', 'OpenStack', 'Ec2']

## 总结

* cloud-init 的配置是通用配置，默认情况下适用于多种云环境。如 OpenStack， GoogleGCE 等
* 日志很重要，很方便进行程序分析
* 镜像还是要自己制作比较好，最好能利用工具做成自动化的。
* 在使用 systemd 服务的系统里，有一部分日志会打到 systemd 里面。需要使用 `journalctl` 来进行查看
* 在第二天的一个培训环境中，我发现有同样的问题，就此看来，这个问题还是很常见并很容易触发。如果有条件，还是修复了得好，要不太影响用户体验了。
