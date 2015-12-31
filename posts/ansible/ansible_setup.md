Title: Ansible安装
Date: 2015-12-30
tags: Ansible
Category: Linux
Slug: ansible-install


由于 Ansible 是通过 SSH 进行通讯的，所以只用安装 master 端就可以了。并不像 puppet/SaltStack 那样在 slave/minion 端进行安装。

由于是用 Python 编写的，安装起来和普通 Python 应用没有太大区别。可以通过源码，pypi, 操作系统的包管理进行安装。

# 系统包管理

## RPM 系

    # install epel source
    yum install -y epel-release
    yum install ansible

## Apt 系
    
```bash
apt-get install -y software-properties-common
apt-add-repository -y ppa:ansible/ansible
apt-get update
apt-get install -y ansible
```

# pypi安装

通过pypi相当简单，直接用pip就可安装

```
pip install ansible
```

# 源码安装

```bash
# download the source from github
# ansible has two git submodules, so the --recursive is required.
git clone git://github.com/ansible/ansible.git --recursive
cd ./ansible

# install
pip install .
```
