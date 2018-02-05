title: 关于虚拟机密码你所有需要知道的一切
slug: everything-about-vm-password
tags: Linux, OpenStack
catagory: OpenStack
date: 2018-01-20


虽然各种云的虚拟机都推荐使用 SSH 密钥登录，但是还是有很多人喜欢使用密码登录，而且有的时候需要通过 console 来登录系统。那么如何更好的设置、修改虚拟机的密码呢?本文以 OpenStack 为例，介绍如何设置及修改虚拟机密码。

## 内置密码

这是最简单的，制作镜像的时候，直接给 root 账号配置一个密码。但是问题也不言而喻。所有的示例都有相同的默认密码，如果用户忘记改的话，其它人很容易的就能扫到你的机器，从而登录你的机器。

## 启动的时候通过 libvirt 进行密码注入

方法是在 `nova.conf` 里面开始如下配置

    [libvirt]
    inject_password = false
    inject_key = false
    inject_partition = -2
    
在虚拟机启动的时候，通过 `--admin-pass` 传入一个指定的密码。但是这个方法也有一系列的问题：

- 不支持 Boot from volume
- 代码层面上，如果注入失败了，没有任何错误信息报出来。
- libvirt 注入对物理机来说并不安全，有安全隐患。
- 密码并没有持久化(存入数据库)，也不应该做持久化，在 `evacuate` 或 `unshelve` 的时候，这些密码信息会被丢掉。

所以这个方法也不是推荐使用，更详细的信息，可能参看我另一篇文章「[rbd 是否支持注入](http://xcodest.me/inject-file-in-rbd.html)」。

## 通过 metadata api 注入

cloud-init 这个服务是从 AWS 学来的。它安装在虚拟机中，在启动虚拟机时，做一些初始化工作。如：硬盘分区自动扩展，SSH Public Key 注入，用户创建等。用户甚至可以注入一些 shell 脚本到虚拟机中运行。在自动化方面启了很大的作用。Heat 的实现就依赖于 cloud-init 服务。

在 OpenStack 上，cloud-init 应该从 http://169.254.169.254 去拿到所需要的信息。而这个服务是通过 iptables 转到了 neutron-metadata-agent 服务上

通过 cloud-init 注入也有几种方式，下面分别来说明。

### 脚本

因为在虚拟机启动的时候，是可以传入 shell 脚本的 user_data，所以可以在这个 shell 脚本里面修改 root 密码。

	cat <<EOF > user_data.sh
	#!/bin/sh
	passwd root<<EOF
	root_pass
	root_pass
	EOF
    
    nova boot --user-data ./user_data.sh --image ...

### cloud init configuration

user data 也可以是 cloud-init 支持的一个 yaml 结构文件，所以还可以通过如下方式改密码

	#cloud-config
    password: password
    chpasswd:
      expire: False

这种方式要比「脚本」的方法优雅一些，推荐使用。而且cloud-init 本身功能很强大，值得深入挖掘下。

### config drive

默认情况下，metadata api 是通过 `http://169.254.169.254` 这个地址获取元数据信息。此外，nova 也支持使用 disk 的方式传入元数据。方便在网络环境不允许 metadata api 的情况下使用。性能也比 metadata api 好的多。

config drive 的开启方法是在 `nova.conf` 中配置：
	
	[DEFAULT]
	force_config_drive = true

或在启动虚拟机的时候，加上如下参数：

	nova boot --config-drive true --image ...
    
开启 config drive 后，除了上面提到的「脚本」和「cloud init configuration」方式，还可以使用 nova 的 `--admin-pass` 参数。虽然这时密码是注入到了虚拟中，但是 cloud init 并不支持读取这里的密码，所以会失败。不过可以修改下 cloud init 支持这种方式。具体更多信息参看[1]。

## 通过 nova set-password

nova 还支持通过 libvirt 的 set-user-password 接口来修改正在运行的虚拟的密码。这个接口本质上是通过 qemu-guest-agent 的 `guest-set-user-password` 接口来修改密码。所以对 libvirt 及 qemu-guest-agent 的版本都有要求。

	libvirt > 1.2.16		   # host
    qemu-guest-agent[2] > 2.3  # linux guest
    qemu-guest-agent[3] > 2.5  # window guest
    
现在看支持的 Guest 操作系统如下：

- CentOS 6 / CentOS 7
- Ubuntu 16.04 / Ubuntu 18.04
- Window XP 及之后所有的版本
    
> 值的一提的是 CentOS 6 虽然用的 qemu-guest-agent 版本是 `qemu-guest-agent-0.12.1.2-2.491.el6_8.6.x86_64`，但是红帽已经把相关 patch backport 了回头，所以也是支持。

使用方法如下：

- 做镜像的时候，安装 qemu-gest-agent 到虚拟机，并且开启随机启动。
- 上传镜像的时候，加上相关的 metadata 信息： `glance image-create --property hw_qemu_guest_agent=yes`

## 虚拟机自动生成加密密码

很早之前，nova 还支持了虚拟机生成密码，然后加密后传回 nova 的功能[4]。其原理如下：

1. 虚拟机动态生成 root 的密码
2. 把 root 密码通过 ssh public key 加密
3. 把加密后的密码通过 `POST /openstack/latest/password` 接口传回 nova
4. 用户通过`nova get-password`命令来拿到密码后的密码
5. 用户使用自己的 ssh private key 进行密码揭密。

因为密钥对等加密原因，除了「1」「5」可以看到明文密码外，其它步骤里面都是加密的。所以这种方式可以说是最安全的方案。连云平台提供商都不能看到真正的密码。

不过这种方式只在 Windows 的 cloud init 版本 cloudbase-init 里面有实现[5]。Linux 版本的 cloud-init 并不支持。不过 Github 上面找到一个类似的实现[6]，虽然只支持 RHEL 7, 但是有需要的话，可以参考修改下。

## 如果我忘记了虚拟机密码怎么办

- 如果你还有虚拟机的 ssh private key，可能通过 ssh 登录机器修改密码
- 如果你的虚拟机平台支持 `nova set-password`, 可以在线改

如果以上都不满足，就需要手动重置 root 密码，基本思路是在 Linux 启动的时候，进入一个不需要密码登录的环境，然后修改 root 密码，步骤如下

1. 通过 horizon, 打开对应虚拟机的 console 界面
2. 软重启虚拟机，
3. 在 grub 界面按字母`e`
4. 找到 `linux` 一行，这一行中加入 `init=/bin/bash`, 并删掉 `console=tty0 console=ttyS0,115200`， 把 `ro` 改为 `rw`
5. 按 `ctrl + x` 继续启动
6. 这时你应试就可以直接登录到系统里面，通过 `passwd` 命令直接修改密码
7. 硬重启操作系统 `nova reboot --hard`

## REF
- [1] <http://niusmallnan.com/_build/html/_templates/openstack/inject_passwd.html#cloud-init>
- [2] <https://github.com/qemu/qemu/commit/215a2771a7b6b29037ee8deba484815d816b6fdd>
- [3] <https://github.com/qemu/qemu/commit/259434b8067e1c61017e9a5b8667b6526b474ff2>
- [4] <https://review.openstack.org/#/c/17274/>
- [5] <https://github.com/openstack/cloudbase-init/blob/master/cloudbaseinit/metadata/services/httpservice.py>
- [6] <https://github.com/vvaldez/openstack-password-reset>
- [0] <https://zhangchenchen.github.io/2017/01/19/openstack-reset-instance-password>
