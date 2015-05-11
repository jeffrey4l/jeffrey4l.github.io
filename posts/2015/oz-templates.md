Title: Oz Templates
Date: 2015-5-11
Category:OpenStack
Tags: OpenStack

最近利用[OZ](https://github.com/clalancette/oz)做了几个常用镜像的自动化制作。回头有用到的会再加进去。说明如下

项目地址: <https://github.com/jeffrey4l/oz-templates>

以下是README里的内容。

## Usage

The isos are located in `/data/isos/`. The isos' name are conversionally.
Including

* CentOS-6.3-x86_64-bin-DVD1.iso
* RHEL-6.3-x86_64-DVD.iso
* ubuntu-14.04.1-server-amd64.iso


```
git clone https://github.com/clalancette/oz.git
cd oz
git clone https://github.com/jeffrey4l/oz-templates.git
cd oz-templates
make all
```

## Detail

The image are configured as following

* without lvm, which will helpful for partion auto extend.
* Default image size is 40GB
* Installed cloud-init with some basic configuration.

