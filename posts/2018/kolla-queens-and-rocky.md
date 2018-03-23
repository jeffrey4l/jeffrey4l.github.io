title: Kolla 从升级到零宕机升级
date: 2018-3-20
slug: kolla-queens-and-rocky
category: OpenStack
tags: OpenStack, Kolla

## Done in Queens

- 镜像构建支持 squash layer, 可以把多个 docker 镜像存储层合并成一层。从而有效的降低镜像存储和传输过程中的资源消耗。
- Ceph 版本从 Jewel 升级到 Luminous， 同时支持了 cephfs 服务及 ceph nfs 服务。Luminous 是 Ceph 最新的长期版本，从去年8月份发布以来，经历了几个小版本的发布，相对来说更加稳定。相比 Jewel， Luminous 在性能上有了彻底性的优化,性能更好。默认使用了异步的消息机制，资源消耗更低。支持多主的 MDS 服务，cephfs 的可用性更高。
- 支持 OpenStack 的 Blazar服务， 该服务是做 OpenStack 服务资源预定的。用户可以在一段时间内申请保留特定类型及数量的资源，以备将来使用。
- 支持 vitrage 服务的部署。Vitrage 是 OpenStack 的问题分析服务。他可能处理 OpenStack 内部 的报警，事件等，然后通过一系统的分析后，向用户展示可见的报告。可以即使的发现问题。并可以配置一些触发流程，自动的恢复系统故障。更加方便 OpenStack 的运行和维护。
- 部分服务支持最小宕机时间升级。Kolla 已经使得 OpenStack 升级变为可能，并且流程也相当简单。这个周期，Kolla 开始朝向怎么保证升级过程中的最小宕机时间，甚至是零宕机努力。现在已经完成了 Cinder 服务和 Keystone 的最小宕机时间的功能。Rocky 周期会完成更多的服务。进一步保证升级的流畅性。
- 支持外部的 DB 服务。在某些使用环境中，数据库可能有专门的机器提供，也有专门的DBA来管理维护。这种情况下，Kolla 就没有必要建立自己的数据库了。通过这个功能，你可以很方便的使用已经存在的数据库实例。
- 支持开发模式。这个对 OpenStack 的开发者很是方便。以住，开发者可能要通过 devstack 搭建完整的 OpenStack 来开发，但是部署复杂，难度高。现在 kolla-ansible 已经支持了开发模式。 通过配置要开发环境的 ``dev_mode``, 如 ``horizon_dev_mode: true``, 那么 horizon 容器内的代码会从物理机上挂载进去，开发者对代码修改后，就可以直接看到修改后的效果。十分方便。

## Plan in Rocky

- 支持 Prometheus 监控。对于复杂的 OpenStack 平台来主产，监控报警必不可少，否则平台难于维护。之前 Kolla 尝试过很多监控平台方案，但是都不是很理想。随着 prometheus 的成熟，Kolla 将其做为自己的默认监控报警方案。整体架构会是 prometheus + alertmanager + gnocchi 的方案，prometheus 用来做数据采集，alertmanager 做通知报警，gnocchi 做数据存储。
- ceph bluestore 支持。在上一个版本中，kolla 中的 ceph 版本已经升级到了 Luminous。但是并没有支持 bluestore 的存储机制，这个版本会把这个功能加上。
- 服务的健康检查。服务的进程状态正常，并不能证明其可以提供服务。需要额外的机制来保证进程服务的可用性。这方面OpenStack社区也有单独的讨论组在寻求解决方案。对于 Kolla 的大部分服务来说，可以通过 docker 支持的 health check 机制来解决。
- 数据备份及恢复。尽管所有的组件都做了高可用，但是一些关键数据的备份还是需要的，防止极端情况的出现。这个周期 Kolla 会提供一个数据库备份及恢复的机制，更好帮助用户做好数据安全。
- 服务的滚动升级。所谓的滚动升级，就是在最小宕机甚至零宕机的情况下进行 OpenStack 平台的升级。这个周期会实现 OpenStack 主要模块的滚动升级。

## 更多信息可以参看 
 
- <https://docs.openstack.org/releasenotes/kolla/queens.html>
- <https://docs.openstack.org/releasenotes/kolla-ansible/queens.html>
- <http://lists.openstack.org/pipermail/openstack-dev/2018-March/128044.html>
