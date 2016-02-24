Title: Kolla Mitaka Midcycle Discuss
Date: 2016-02-16
Slug: kolla-mitaka-midcycle-discuss
Tags: Kolla
Category: OpenStack

[TOC]

2016年2月9日-10日，Kolla Team 举办了 Mitaka 的中期会议，对遇到的问题、解决的方法及接下来的工作内容做了深入讨论。

# 讨论的优先级安排

首先对本次讨论进行了优先级安排[^1]。

* Upgrades： 这是现在的重中之重。如何能对现有的Kolla进行平滑的升级。包括 OpenStack 组件和基础服务组件(如 MariaDB 等)。
* diagnostics/logging: 主要是指 ELK。
* stability of deployment
* Security
* backwards compatibility
* selinux
* kolla-ansible split

# Upgrade

升级主要涉及到两部分。相关的BP在这里[^3]。

1. 是OpenStack的各个组件
2. 是一些基础服务组件。

## OpenStack 组件

由于 OpenStack 各个组件的结构基本相同，都是有DB, API, Scheduler等几个部分构成。所以这里的升级要简单一些，而且已经基本完成了编码工作，不过需要大量的测试来保证升级的可靠性[^2]。

## 基础服务组件

由于各个组件的升级方式并不同，同一个组件不同版本间，可能也不相同。所以这部分相比较来说要困难的多。讨论中对各个组件进行了逐一讨论。包括升级的方式，有可能造成的影响等。详细信息见[^4]

# Diagnostics/Logging

# Security

安全也是很重要的事情，Team 两次讨论了这个问题[^5][^8]

在各个模块之前开启 SSL 功能[^5]。当然默认是通过配置开启的。这样使 OpenStack 运行在一个更加安全的环境中。这个功能期望是在 Mitaka-3 中完成。

容器中的安全

* 使用非 root 用户运行服务
* Container 内，配置文件是否能被修改
* rootwrap 不应该能修改
* 开启 SELinux 

# Backport

Liberty 是 Kolla Release 的第一个版本。而在现在的 Master 分支中，已经有了大量的新功能。Team 讨论了 Backport 的原因和意义[^6]。

最主要的原因

* Ansible 的 docker 模块有bug, 导致 ansible 与 1.8.2 以上的 docker 版本不兼容
* docker 1.9 后的named volume 功能很好的解决了
    1. 可能出现在数据丢失。在使用 data container 时，如果 Base Image 发生改变，data container 也会被重新创建，从而造成数据丢失。
    2. 可能造成短时间的网络不可用。原因也是 data container 里面创建的 namespace 会被删除。

解决方法有三种：

* 直接把 stable/liberty 分支移动到 master 的位置。但是个人感觉不靠谱。
* 把所有的 commmit squash 后提交到 stable/liberty 分支上
* stable/liberty 和 master 做一次 merge。
* 只 backport kolla_docker module

现在看来，应该会采取方法 4。

# kolla code sharing

现在 Kolla 相关的项目有两个 https://github.com/openstack/kolla 和 https://github.com/openstack/kolla-mesos 。将来还会分拆出一个 kolla-ansible 项目来。现在， 单这两个项目下就有很多的重复代码，导致做了许多 copy, paster 的工作。这个 topic[^9] 就是来解决这个问题的。

重复的东西

* extend_start.sh 在两个仓库中有很多重复的
* kolla_docker 等 ansible 模块
* 很多 config 里面的定义

可能的解决方法包括:

* 定期的把 `<kolla>/ansible` 下的模板复制到 kolla-mesos 中
* 两连都存在副本，定期进行双向的同步。
* 创新一个新的仓库包含一些共用的模板

# Roadmap

Mitaka, Netron, Ocata， P版本的功路线图[^7]。你更期待什么功能呢?

## Mitaka-3 Roadmap

Mitaka 进入最后的阶段，还有一些重要功能在开发中，现在主要还有以下几点。

- diagnostics
- reconfigure services on a redeploy
- infrastructure services upgrades such as mariadb
- migration path for data volumes
- functional tests in gate (boot a vm &amp; ping test)

## Newton Roadmap
- voting gates
- jumbo frames MTU investigation
- kolla as replacement of devstack (bindmount sources etc)
- code dedupe between mesos/ansible (general templates)
- ansible 2.0+
- conditionalize docs
- selinux
- more functional tests in gates (mitaka will have boot an vm)
- documentation specifically operator guides
- network isolation documentation
- multinode gates
- mechanism to build/push stable images to dockerhub
    - push per tag
    - nightly push
- kolla-ansible split right at start of newton split the repos
- hot-reload of running config for openstack service
- Python API with no running services for managing Kolla
- BiFrost documentation and investigation

## Ocata Roadmap

- deploy full big tent (or develop plugin mechanism to deploy whatever) / maybe we could do a skeleton service
- kolla-saltstack, kolla-puppet investigation - may not even be needed when moving to Ansible 2.0
- horizon, neutron, and nova plugin support - this exists already? would like to do in Newton but not have bandwidth
- Monitoring
- Backup and Restore of OpenStack data
- Data caching (e.g. redis)
- kolla-kubernetes
- runc investigation
- rkt investigation

## P Roadmap

- rollback support from upgrade
- canary deployment
- make Kolla operate optionally without net=host for upcoming kolla-mesos and kolla-kubernetes repositories


# REF

[^1]: <https://etherpad.openstack.org/p/kolla-mitaka-midcycle-priorities>
[^2]: <https://etherpad.openstack.org/p/kolla-mitaka-midcycle-upgrades>
[^3]: <https://blueprints.launchpad.net/kolla?searchtext=upgrade>
[^4]: <https://etherpad.openstack.org/p/kolla-mitaka-midcycle-infrastructure-upgrades>
[^5]: <https://etherpad.openstack.org/p/kolla-mitaka-midcycle-ssl>
[^6]: <https://etherpad.openstack.org/p/kolla-mitaka-midcycle-backport>
[^7]: <https://etherpad.openstack.org/p/kolla-mitaka-midcycle-roadmap>
[^8]: <https://etherpad.openstack.org/p/kolla-mitaka-midcycle-security>
[^9]: <https://etherpad.openstack.org/p/kolla-mitaka-midcycle-kolla-code-sharing>
