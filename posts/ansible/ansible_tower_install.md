Title: Install Ansible Tower
Date: 2015-12-31
Tags: Ansible Tower
Category: Linux
Slug: install-ansible-tower

[TOC]

# 手动安装

## 下载安装包

从 http://www.ansible.com/tower-trial 下载，需要填个人信息，提交后会自动下载。

把安装包复制到要安装的机器中去，解压准备安装

```
tar xvf ansible-tower-setup-latest.tar.gz
cd ansible-tower-setup-2.4.3
```

这个安装包本质上是一个playbook。其中`configure`是用来生成配置文件的脚本，运行它会有几个问题，让你回答，回答完后就开始自动安装了。也可把这些问答写到一个文件中，让其自动化。建立名为`tower_setup_conf.yml` 的文件，其内容为:

```yaml
admin_password: password
database: internal
munin_password: password
pg_password: password
primary_machine: localhost
redis_password: password
```

开始进行设置

```
./configure --options-file tower_setup_conf.yml
```

如果没有问题，脚本会提示：

```
The configuration provided in tower_setup_conf.yml appears complete.

FINISHED!
You have completed the setup wizard. You may execute the installation of
Ansible Tower by issuing the following command:

sudo ./setup.sh
```

运行安装脚本

```
sudo ./setup.sh
```

其主要工作为

1. 如果没有安装ansible, 就安装上ansible
2. 使用ansible进行tower的安装

安装好后，终端会提示给你访问的地址，用浏览器打开就可以了。输入上面设置的admin账号密码登录。

之后会出现设置 Tower License 的界面。可以从 http://www.ansible.com/license 申请到一个10个节点的免费 license。最后把 License 复制进去提交就可以了。

# 使用 Vagrant 进行安装

官方提供 Vagrant Images, 方便进行安装测试。使用方法

```
vagrant init tower http://vms.ansible.com/ansible-tower-2.4.3-virtualbox.box
vagrant up
vagrant ssh
```

# REF

* http://docs.ansible.com/ansible-tower/latest/html/installandreference/tower_installer.html
* http://docs.ansible.com/ansible-tower/latest/html/installandreference/tower_install_wizard.html
