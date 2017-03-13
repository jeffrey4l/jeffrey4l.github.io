OpenStack Ocata Releasenotes
############################

:date: 2017-03-12
:tags: OpenStack
:slug: openstack-ocata-releasenotes

Nova
====

* Ocata 版本加入了许多 Cell V2 的功能。但是不是所有的都可以用于生产。现在部署 Nova 需要最少创建一个 Cell。
* FilterScheduler 只能基于 Placement 服务做调度。现在只支持CPU, RAM 和 Disk 资源。将来会支持更多资源类型。
* Nova api 的 microversion 版本支持到 v2.42. 
* 增加了一个 nova-status 命令，方便运维人员做升级检查
* 增加对 OSProfiler 工具的支持。方便分析 OpenStack 控制平面的性能。
* serial console 支持 ironic。
* Vlan tags 信息可以通过 metadata 服务获取。
* 增强 Hyer-V 的支持。
* 增强对 Virtuozzo 的支持。

Keystone
========

* Fernet 成为默认的 Token Provider
* PKI 和 PKIz token provider 被移除。
* 增加 OSProfile 支持。

Glance
======

* 支持无宕机的数据库升级
* Minor Version API 升级到 2.5
* 镜像可见性增加 community 选项。
* 支持 ploop 格式的镜像

Cinder
======

* 增加 Active-Active 的高可用支持(实验)。
* 大量的 Driver 增强，包括: Dell SC，Ceph, Datera, Hitachi 等。

Neutron
=======

* Linux Bridge agent 支持 QoS DSCP。
* Resource tag 机制支持 subnet, port, subnetpool 和 router.
* 增加对 Placement API 的支持。
* 增加 neutron-netns-cleanup 工具进行 namespace 清理。
* 支持 oslo.privsep 

Ceilometer
==========

* 增加对 Cinder volume, snapshot 和 backup 大小的计量。
* 通过 libvirt api 来获取 metadata 信息，不用再请求 Nova API。
* 废弃 ceilometer-api 和 ceilometer-collector。

Heat
====

* 增加 OS::Aodh::CompositeAlarm
* 增加 OS::Cinder::QoSAssociation
* 增加 OS::Designate::Zone 和 OS::Designate::RecordSet 
* 增加 OS::Keystone::Domain
* 增加 OS::Neutron::Quota 
* 增加 OS::Nova::Quota
* 增加 OS::Sahara::Job
* 增加 OS::Zaqar::Notification 和 OS::Zaqar::MistralTrigger

Horizon
=======

* 支持 Keystone to keystone feration。
* Access & Security 移到了单独的 panel 里面
* 增加对 osprofiler 的支持

Ironic
======

* Port Group 允许用户做 Bond
* API 支持 power off, soft reboot 和 sending non-maskable interrupts
* 删除 AMT, iBoot, msftocs, seamicro, VirtualBox, and Wake-On-Lan 驱动。
* Ironic API 支持审计
* 增加对 Dynamic Driver 的支持。
* 支持从一个 conductor 节点部署不同CPU 类型的机器.
* 支持 OneView Driver.


Sahara
======

* 支持 Kafka MapR 插件
* 支持 CDH 5.9.0

Kolla
=====

* 增加 Freezer, Karbor, Monasca, Panko, Zun, Redis 等镜像构建
* 支持用户指定 policy.json 文件。
* 增加 kolla-host 命令，用来初始化系统及安装 docker。
* 增加静态 uid, gid 支持。
* 实现部署 Designate, Cloudkitty, Panko, Ocatavia, Collectd 等服务
