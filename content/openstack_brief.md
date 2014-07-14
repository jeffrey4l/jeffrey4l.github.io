title: Openstack Brief
date: 2013-06-17 23:08
tags: openstack


自从Openstack诞生之日起，就受到越来越多的开发者，用户的关注。整个代码的规模和质量正在飞速的发展。随着各种功能的增加，Openstack下面已经拥有了相当多子项目，来完成各种各样的功能。本文将简单介绍各个子项目的功能和发展。所有的项目现状是基于Grizzly的版本来写的。

* Keystone
* Nova
* Cinder
* Glance
* Openstack Network(Quantum)
* LBaaS
* Ceilometer
* Baremetal

# Keystone

keystone是Openstack的认证和服务注册模块。其结构比较简单。其功能包括:

1. **认证** 主要功能是管理用户和用户组的信息，后端可以绑定ldap, mysql等认证方式。
2. __服务注册模块__ 主要用于管理Openstack相关服务的地址，所有的服务都要先注册到Keystone中，才可以使用。它可使用基于文件的模板，也可以使用数据库存储。
3.  __Token__ 管理。

相对于其它子项目来说，keystone最近的变化并不是太大。将来一个比较大的变化就是基于domain的权限控制，届时Tenant里也可以细经出管理员和使用者的角色，并有详细的权限功能控制。

# Nova

Nova是Openstack最早的子项目。现在其它项目如cinder, quantum(Openstack Network)都是来自于该项目。可以说这是Openstack中最复杂，最主要的部分。它负责

1. 用户接口(nova-api)。处理来自于用户的请求，并做出合理的响应。
2. 计算调度(nova-scheduler)。用于在物理之前进行资源的调配。
3. 虚拟化的管理(nova-compute)。管理虚拟机的适配接口。通过它可以管理真实的虚拟技术驱动的机器，如KVM, XEN, Hypervisor V等。

当然还有一些功能如nova-network, nova-volume已经从nova项目中迁移出来，成为独立的子项目。将来一段时间的变化，主要集中在nova-network的废弃，nova-conductor的更加完善，新的api(v3)的支持，对于祼机的支持。

# Cinder

Cinder是由nova-volume分化而来，用于管理虚拟机的块存储(block storage), 类似AWS的EBS。其功能主要是创建，维护，删除块存储。后端可以使用LVM, glusterFs, Ceph, NFS等软件技术的存储，也可以使用NetApp, Huawei，IBM等商用解决方案。当然也可以自己编写自己存储的Driver来支持更多的存储类型。

# Glance

Glance用于管理各种系统的镜像。他后端也可以配置各种存储方案。包括本地，swift, ceph等。

# Openstack Network.

(Quantum名称因为商标问题停用）。

网络基本是Openstack最复杂的模块，涉及到的技术和协议相当多，也最容易出问题。也正因为此，很有必要将网络模块从越来越笨重的nova的拿出来。

Openstack Network提示了强大的网络服务（Network-as-a-service),用来实现L2, L3层的网络。在原有的nova-network的基础之上，增加了相当多的功能

1. 加上了xvlan, gre等网络技术，并可以编写自己的插件，来增加其功能
2. 使用者可以创建更加丰富的网络模型，如私用路由器等
3. 为Qos, 流量监控等提供支持。

现在Quantum还有一些问题，如HA方案不成熟，不太适用于Production。不过根据社区的计划，下一个版本(H)将会把nova-network废弃掉。所以Quantum才是真正的趋势。现在很有必要将其吃透。

# LBaaS

Load-Balancer-as-a-service.在Quantum基础上实现的负载均衡。后端既可以使用haproxy,也可以使用cisco, f5等硬件。（不过我还没有功能搭建过这个服务。

# Ceilometer

Openstack的计量，计费模块。可以统计Cpu, IO, Network使用的详细情况。对公有云和私有云都有极大的好处。现在也有一个Horizon的插件，可以直接在dashboard里显示使用情况（将来，该插件会合并到horizon中）

#Baremetal

增加Openstack对裸机的管理功能。可以实现直接对裸机进行系统安装，配置。模糊了虚拟化和物理机之间的界线。现在所有模块包括nova, glance, cinder都在努力增强这方面的功能。
这个模块，我更期望是可以建立Nested-Openstack。同一个Openstack环境，既管理物理机，又自动在物理机上安装Openstack的模块来成为Openstack的一部分。
