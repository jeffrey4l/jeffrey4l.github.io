title: OpenStack Kolla AIO Install
date: 2016-1-31
tags: Kolla, OpenStack
category: OpenStack
slug: kolla-aio-install

[TOC]


Kolla 依赖于以下几个主要组件

* Ansible &gt; 1.9.4, &lt; 2.0
* Docker &gt; 1.9.0
* docker-py &gt; 1.6.0
* python jinja2 &gt; 2.6.0

几点说明：

* 机器使用的是 kvm 虚拟机进行的测试。配置上使用 4G RAM, 2 CPU, 2 网卡的配置
* 由于使用了 Docker，所以对于底层系统并还没什么要求，本文使用 CentOS 7 系统。
* Kolla master 分支上使用的是 RDO master 上的源，打包极不稳定，时常会有 Bug 出现。所以本文使用的是 CentOS + 源码的安装方式
* 由于国内网络原因，一些国外的源(这些源还没有国内镜像)会相当慢，所以 build docker image 时会很慢，推荐使用 VPN

# 安装

安装好操作系统后，依次进行如下配置

## 源

加入 Docker 的源

```
sudo tee /etc/yum.repos.d/docker.repo << 'EOF'
[dockerrepo]
name=Docker Repository
baseurl=https://yum.dockerproject.org/repo/main/centos/$releasever/
enabled=1
gpgcheck=1
gpgkey=https://yum.dockerproject.org/gpg
EOF
```

加入 EPEL 源

```
yum install -y epel-release
```

## 安装 Kolla 所需依赖

```
yum install -y ansible docker-engine git gcc python-setuptools
easy_install -U pip
```

并启动 Docker 服务

```
systemctl enable docker
systemctl start docker
```

## 下载 Kolla 代码并安装依赖

```
git clone https://github.com/openstack/kolla.git
cd kolla
pip install -r requirements.txt -r test-requirements.txt tox
```

# Build Docker Image

以下如果没有特别说明，所有的操作都是在 Kolla 项目的目录里进行

首先要先生成并修改配置文件

```
tox -e genconfig
cp -rv etc/kolla /etc/
```

然后修改 `/etc/kolla/kolla-build.conf` 文件，它是用来控制 kolla build 过程的。修改后，其主要内容如下:

```
[DEFAULT]
base = centos
install_type = soruce
namespace = lokolla
push = false
```

接下来就是进行漫长的 build, 这个过程主要依赖机器性能和网速。如果快的话，20多分钟就完成。如果有问题的话，会很久。不过依赖于 Docker Build 的 Cache 功能，就算重跑的话，之前已经 Build 好的也会很快完成。

```
./tool/build.py -p main
```

参数中的 `-p main` 是指定了只 build 主要的 image, 包括: cinder, ceilometer, glance, heat, horizon, keystone, neutron, nova, swift. 这些可以只生成的 `kolla-build.conf` 里找到。

如果 Build 完成之后，使用 `docker images` 能看到所有已经 build 好的镜像。

# Deploy

依然是先修改配置文件，与 Deploy 相关的主要是两个配置文件 `/etc/kolla/passwords.yml` 和 `/etc/kolla/globals.yml`。他们为 ansible 提供一些变量的设定。主要需要修改的是 `globals.yml` 文件。修改后，其主要内容为:

```yaml
config_strategy: "COPY_ALWAYS"

kolla_base_distro: "centos"
kolla_install_type: "source"
kolla_internal_address: "10.2.0.254"

network_interface: "eth0"
neutron_external_interface: "eth1"
openstack_logging_debug: "true"

enable_cinder: "no"
enable_heat: "no"
```

kolla 使用一个名为 `kolla-ansible` 的封装脚本， 并提供以下几个命令

```
./tools/kolla-ansible -h
Usage: ./tools/kolla-ansible COMMAND [options]

Options:
    --inventory, -i <inventory_path> Specify path to ansible inventory file
    --playbook, -p <playbook_path>   Specify path to ansible playbook file
    --keyfile, -k <key_file>         Specify path to ansible vault keyfile
    --help, -h                       Show this usage information
    --tags, -t <tags>                Only run plays and tasks tagged with these values

Commands:
    prechecks    Do pre-deployment checks for hosts
    deploy       Deploy and start all kolla containers
    post-deploy  Do post deploy on deploy node
    pull         Pull all images for containers (only pulls, no runnnig container changes)
```

可以使用 `./tools/kolla-ansible prechecks` 来检查一个机器是否满足安装条件。

使用 `./tools/kolla-ansible deploy` 来开始正式安装。安装会很快，我机器上，几分钟就安装完成了。

最后，使用`./tools/kolla-ansible post-deploy` 来生成 `/etc/kolla/admin-openrc.sh` 文件用来加载认证变量。

# 查看安装后的状态

```
$ docker ps
IMAGE                                                   COMMAND                 STATUS              PORTS               NAMES
lokolla/centos-source-horizon:2.0.0                     "kolla_start"           Up 15 minutes                           horizon
lokolla/centos-source-heat-engine:2.0.0                 "kolla_start"           Up 16 minutes                           heat_engine
lokolla/centos-source-heat-api-cfn:2.0.0                "kolla_start"           Up 16 minutes                           heat_api_cfn
lokolla/centos-source-heat-api:2.0.0                    "kolla_start"           Up 16 minutes                           heat_api
lokolla/centos-source-neutron-agents:2.0.0              "/start.sh"             Up 16 minutes                           neutron_agents
lokolla/centos-source-neutron-openvswitch-agent:2.0.0   "kolla_start"           Up 16 minutes                           neutron_openvswitch_agent
lokolla/centos-source-neutron-server:2.0.0              "kolla_start"           Up 16 minutes                           neutron_server
lokolla/centos-source-openvswitch-vswitchd:2.0.0        "kolla_start"           Up 16 minutes                           openvswitch_vswitchd
lokolla/centos-source-openvswitch-db-server:2.0.0       "kolla_start"           Up 16 minutes                           openvswitch_db
lokolla/centos-source-nova-compute:2.0.0                "kolla_start"           Up 17 minutes                           nova_compute
lokolla/centos-source-nova-scheduler:2.0.0              "kolla_start"           Up 17 minutes                           nova_scheduler
lokolla/centos-source-nova-novncproxy:2.0.0             "kolla_start"           Up 17 minutes                           nova_novncproxy
lokolla/centos-source-nova-consoleauth:2.0.0            "kolla_start"           Up 17 minutes                           nova_consoleauth
lokolla/centos-source-nova-conductor:2.0.0              "kolla_start"           Up 17 minutes                           nova_conductor
lokolla/centos-source-nova-api:2.0.0                    "kolla_start"           Up 17 minutes                           nova_api
lokolla/centos-source-nova-libvirt:2.0.0                "kolla_start"           Up 17 minutes                           nova_libvirt
lokolla/centos-source-glance-api:2.0.0                  "kolla_start"           Up 17 minutes                           glance_api
lokolla/centos-source-glance-registry:2.0.0             "kolla_start"           Up 17 minutes                           glance_registry
lokolla/centos-source-keystone:2.0.0                    "kolla_start"           Up 18 minutes                           keystone
lokolla/centos-source-rabbitmq:2.0.0                    "kolla_start"           Up 18 minutes                           rabbitmq
lokolla/centos-source-data:2.0.0                        "/bin/sleep infinity"   Up 18 minutes                           rabbitmq_data
lokolla/centos-source-mariadb:2.0.0                     "kolla_start"           Up 19 minutes                           mariadb
lokolla/centos-source-memcached:2.0.0                   "kolla_start"           Up 19 minutes                           memcached
lokolla/centos-source-haproxy:2.0.0                     "kolla_start"           Up 20 minutes                           haproxy
lokolla/centos-source-keepalived:2.0.0                  "kolla_start"           Up 20 minutes                           keepalived
lokolla/centos-source-kolla-ansible:2.0.0               "/bin/sleep infinity"   Up 20 minutes                           kolla_ansible
lokolla/centos-source-rsyslog:2.0.0                     "kolla_start"           Up 20 minutes                           rsyslog
```

为了显示好看，我去掉了一些无关的列。通过上面，可以看出

* 多数 container 里是由 kolla_start 这个脚本启动起来的
* 由于 kolla 使用的是 `--net=host` 网络，所以没有必要做端口映射
* 每个模块拆分成了多个container, 如 nova 被拆分成了nova_api, nova_libvirt, nova_conductor, nova_novncproxy, nova_compute等多个 container。很好的遵守了一个容器一个进程的原则。
