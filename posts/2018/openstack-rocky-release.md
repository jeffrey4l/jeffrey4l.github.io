title: OpenStack Rocky Release
date: 2018-9-10
category: OpenStack
tags: Linux OpenStack
status: draft


## Glance

* 增加了和 cinder 一样多后端存储的支持。当需要配置多个后端存储时，不用像之前一样，只能配置多个 glance 服务了。
* 支持了镜像格式的自动转换。之前 glance 有一套 tasks API, 可以创建一个后台任务，可以用来做镜像自动转化，但是使用起来比较复杂[1]。需要管理员修改配置文件，而且需要使用单独的 Task Create 接口。现在如果打开这个功能后，当用户使用 image import 接口时，会自动的做镜像的格式转换[1]。
* Glance 一直使用 md5 做为 checksum 字段的算法，用于数据效验和防篡改。但是 md5 已经被证明是不安全的算法。新版本可以通过修改配置文件的方式，使用更加安全的算法[^3]。

## Nova

* 增加了对 AArch64 处理的支持
* 支持动态的开启或关闭某个 cell
* nova placement api 增加了 member\_of 参数，完善了对 resource provider 聚合的支持。
* 自动向 placement 服务中上报 CPU 的特征信息，可用于细粒度的虚拟机调度
* nova placement 服务增加了角色控制
* ironic driver 支持进入 rescue 模式进行机器修复
* virtio-net 驱动支持多队列，提升网络性能
* libvirt driver 增加对 NVMe, ScaleIO 存储的支持。
* libvirt driver 增强对 Cinder 前端 QoS 的支持，包括 quota:read\_bytes\_sec\_max, quota:write\_bytes\_sec\_max 等
* 支持配置 neutron 网络的 NUMA 亲和性
* PowerVM driver 支持热插拔网卡，虚拟机快照， vSCSI FC。

## kolla

* 增加 Apache Storm, Logstash 5.x, Monasca Thresh, radvd, prometheus, cadvisor 等镜像
* horizon 镜像增加了 blazar, congress, octavia 界面的支持
* 支持 Ceph Bluestore 的部署
* 支持 Monasca Log Persister 和 Monasa Log Transformer 部署。
* 支持关闭 nova\_ssh 容器
* 默认配置 mariadb binary logs 有效时间为 14天
* 支持 Prometheus/AlertManager/Node Exporter/ 的部署
* 支持额外的 ml2 配置文件
* 支持 Glance 的零宕机升级



[^1]: https://www.sebastien-han.fr/blog/2015/05/11/openstack-glance-a-first-glimpse-at-image-conversion/
[^2]: https://review.openstack.org/572515
[^3]: https://review.openstack.org/587225
[^4]: https://docs.openstack.org/releasenotes/nova/rocky.html
[^5]: https://docs.openstack.org/releasenotes/kolla/rocky.html
[^6]: https://docs.openstack.org/releasenotes/kolla-ansible/rocky.html
