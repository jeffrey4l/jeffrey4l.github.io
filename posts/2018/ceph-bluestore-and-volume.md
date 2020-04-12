---
title: Ceph bluestore 和 ceph-volume
date: 2018-04-07
modified: 2018-11-25
slug: ceph-bluestore-and-ceph-volume
tags: Ceph
category: Ceph
---

## 部署

使用环境

- 单节点
- CentOS 7.4
- 使用 ceph-deploy 进行部署

准备 centos 7.4 系统的机器，并配置好 ssh 的无密码登录

安装 ceph-deploy

```
$ yum install https://download.ceph.com/rpm-luminous/el7/noarch/ceph-deploy-2.0.0-0.noarch.rpm
```

数据 ceph 安装包

```console
$ mkdir ceph-install
$ cd ceph-install
$ ceph-deploy new node1
```

把如下内容加入到 ceph.conf 里面，把默认的副本数据调成1。

```ini
[global]
osd pool default size = 1
osd pool default min size = 1
```

安装 ceph 包

```console
$ ceph-deploy install --release luminous node2
```

初始化 mon

```console
$ ceph-deploy mon create-initial
$ ceph-deploy admin node1
```

这时 ceph 已经可以访问了

```console
$ ceph -s
  cluster:
    id:     5b2f0020-fc24-44de-a6c9-a88efdc5074f
  health: HEALTH_OK
  services:
    mon: 1 daemons, quorum node1
    mgr: no daemons active
    osd: 0 osds: 0 up, 0 in

  data:
    pools:   0 pools, 0 pgs
    objects: 0 objects, 0 bytes
    usage:   0 kB used, 0 kB / 0 kB avail
    pgs:
```

接下来要部署 ceph mgr, 这个组件在 Luminous 里面是必装组件

```console
$ ceph-deploy  mgr create node1
```

接下来部署 ceph osd, 现在推荐使用 ceph-volume lvm 来管理磁盘。所有安装的时候 ，就需要准备一个 lv 出来。为了测试 bluestore 的 block.db 和 block.wal， 我们来做三个lv 分别用于单 osd 。

```console
$ uuid=$(uuidgen)
20861703-1a01-415c-97c3-7e855cfb8994
$ pv create /dev/sdb
Physical volume "/dev/sdb" successfully created.
$ vgcreate ceph-$uuid /dev/sdb
Volume group "ceph-20861703-1a01-415c-97c3-7e855cfb8994" successfully created
$ lvcreate ceph-$uuid -L 1G -n osd.wal
Logical volume "osd.wal" created.
$ lvcreate ceph-$uuid -L 1G -n osd.db
Logical volume "osd.db" created.
$ lvcreate ceph-$uuid -l 100%FREE -n osd.block
Logical volume "osd.block" created.
```

接下来，就可以创建 OSD 了。

```console
# 使用 ceph-deploy 部署
$ ceph-deploy osd create \
    --bluestore \
    --data ceph-$uuid/osd.block \
    --block.db ceph-$uuid/osd.db \
    --block.wal ceph-$uuid/osd.wal
    node1

# 使用 ceph-volmue 部署
$ ceph-volume lvm create \
    --data ceph-$uuid/osd.block \
    --block.db ceph-$uuid/osd.db \
    --block.wal ceph-$uuid/osd.wal
```

这样，一个最小的集群就建好了

```console
$ ceph -s
  cluster:
    id:     5b2f0020-fc24-44de-a6c9-a88efdc5074f
    health: HEALTH_OK

  services:
    mon: 1 daemons, quorum node1
    mgr: node2(active)
    osd: 1 osds: 1 up, 1 in

  data:
    pools:   0 pools, 0 pgs
    objects: 0 objects, 0 bytes
    usage:   2048 MB used, 37883 MB / 39931 MB avail
    pgs:

$ ls -alh /var/lib/ceph/osd/ceph-0/
total 52K
-rw-r--r-- 1 ceph ceph 409 Apr 12 03:05 activate.monmap
lrwxrwxrwx 1 ceph ceph  56 Apr 12 03:05 block -> /dev/ceph-20861703-1a01-415c-97c3-7e855cfb8994/osd.block
lrwxrwxrwx 1 ceph ceph  53 Apr 12 03:05 block.db -> /dev/ceph-20861703-1a01-415c-97c3-7e855cfb8994/osd.db
lrwxrwxrwx 1 ceph ceph  54 Apr 12 03:05 block.wal -> /dev/ceph-20861703-1a01-415c-97c3-7e855cfb8994/osd.wal
-rw-r--r-- 1 ceph ceph   2 Apr 12 03:05 bluefs
-rw-r--r-- 1 ceph ceph  37 Apr 12 03:05 ceph_fsid
-rw-r--r-- 1 ceph ceph  37 Apr 12 03:05 fsid
-rw------- 1 ceph ceph  55 Apr 12 03:05 keyring
-rw-r--r-- 1 ceph ceph   8 Apr 12 03:05 kv_backend
-rw-r--r-- 1 ceph ceph  21 Apr 12 03:05 magic
-rw-r--r-- 1 ceph ceph   4 Apr 12 03:05 mkfs_done
-rw-r--r-- 1 ceph ceph  41 Apr 12 03:05 osd_key
-rw-r--r-- 1 ceph ceph   6 Apr 12 03:05 ready
-rw-r--r-- 1 ceph ceph   3 Apr 12 03:05 require_osd_release
-rw-r--r-- 1 ceph ceph  10 Apr 12 03:05 type
-rw-r--r-- 1 ceph ceph   2 Apr 12 03:05 whoami
```

## bluestore & rocksdb & ceph-volume

ceph 的组件多采用插件的机制，包括后端存储，KV 数据库，磁盘管理等。各组件之间可以灵活的组合。

基于后端存储包括 filestore, kvstore，memstore 和新的 bluestore。 Ceph Luminous 引用了 bluestore 的存储类型，不依赖文件系统，直接管理物理磁盘，相比filestore, 在 io 写入的时候路径更短，也避免了二次写入的问题，性能会更加好。

KV 存储主要包括 LevelDB, MemDB 和新的 RocksDB。 RocksDB 是 Facebook 基于 LevelDB 开发的 key-value 数据，并对闪存(flash)有更友好的优化。

磁盘管理之前只有个 ceph-disk, 现在新引入了 ceph-volume。基于 lvm 来管理磁盘，并会逐渐废弃掉 ceph-disk。

![ceph-bluestore.png](images/2018/ceph-bluestore.png)

基中比较有意思的是 RocksDB 的实现，RocksDB 原本只基于文件系统的。但是得益于它本身的灵活性，bluestore 实现了一套 RocksDB 的 Env 接口，还在 BlueStore 上面实现了一套 BlueFS 的接口与 BluestoreEnv 对接。使得 RocksDB 可以存储在 BlueStore 上面。

## wal & db 的大小问题

在 ceph bluestore 的情况下，wal 是 RocksDB 的 write-ahead log, 相当于之前的 journal 数据，db 是 RocksDB 的 metadata 信息。在磁盘选择原则是 block.wal > block.db > block。当然所有的数据也可以放到同一块盘上。

默认情况下， wal 和 db 的大小分别是 512 MB 和 1GB, 包括 [Sage Weil 的 PPT ](https://www.slideshare.net/sageweil1/bluestore-a-new-storage-backend-for-ceph-one-year-in)里面也是这样标明的。现在没有一个太好的理论值，它和 ceph 里面的每个 OSD 里面的对象个数有关系。更多讨论可以[参看](http://lists.ceph.com/pipermail/ceph-users-ceph.com/2017-September/020822.html)。 现在社区推荐的是 block size * 4% 的值。也就是说如果你的 block 盘大小是 1TB，那 block.db 的大小最少是 40GB。具体参看[bluestore-config-ref#sizing](http://docs.ceph.com/docs/master/rados/configuration/bluestore-config-ref/#sizing)，[[ceph-users] WAL/DB size](http://lists.ceph.com/pipermail/ceph-users-ceph.com/2018-September/029643.html)

值得注意的是，如果所有的数据都在单块盘上，那是没有必要指定 wal & db 的大小的。如果 wal & db 是在不同的盘上，由于 wal/db 一般都会分的比较小，是有满的可能性的。如果满了，这些数据会迁移到下一个快的盘上(wal - db - main)。所以最少不会因为数据满了，而[造成无法写入](http://lists.ceph.com/pipermail/ceph-users-ceph.com/2017-September/021037.html)。


## 使用 bluestore 时的 osd 分区

如果是使用的 ceph-disk 管理磁盘，他会建立一个 100MB 的分区，来存放 keyring / whoami 这些信息，这和之前的逻辑是一样的。

如果是使用 ceph-volume 管理磁盘，`/var/lib/ceph/osd/ceph-0` 分区会从 tmpfs 挂载过来(也就是内存)

```console
$ mount | grep osd
tmpfs on /var/lib/ceph/osd/ceph-0 type tmpfs (rw,relatime)
$ ls -Alh /var/lib/ceph/osd/ceph-0
-rw-r--r-- 1 ceph ceph 409 Apr 12 03:05 activate.monmap
lrwxrwxrwx 1 ceph ceph  56 Apr 12 03:05 block -> /dev/ceph-20861703-1a01-415c-97c3-7e855cfb8994/osd.block
lrwxrwxrwx 1 ceph ceph  53 Apr 12 03:05 block.db -> /dev/ceph-20861703-1a01-415c-97c3-7e855cfb8994/osd.db
lrwxrwxrwx 1 ceph ceph  54 Apr 12 03:05 block.wal -> /dev/ceph-20861703-1a01-415c-97c3-7e855cfb8994/osd.wal
-rw-r--r-- 1 ceph ceph   2 Apr 12 03:05 bluefs
-rw-r--r-- 1 ceph ceph  37 Apr 12 03:05 ceph_fsid
-rw-r--r-- 1 ceph ceph  37 Apr 12 03:05 fsid
-rw------- 1 ceph ceph  55 Apr 12 03:05 keyring
-rw-r--r-- 1 ceph ceph   8 Apr 12 03:05 kv_backend
-rw-r--r-- 1 ceph ceph  21 Apr 12 03:05 magic
-rw-r--r-- 1 ceph ceph   4 Apr 12 03:05 mkfs_done
-rw-r--r-- 1 ceph ceph  41 Apr 12 03:05 osd_key
-rw-r--r-- 1 ceph ceph   6 Apr 12 03:05 ready
-rw-r--r-- 1 ceph ceph   3 Apr 12 03:05 require_osd_release
-rw-r--r-- 1 ceph ceph  10 Apr 12 03:05 type
-rw-r--r-- 1 ceph ceph   2 Apr 12 03:05 whoami
```

至于目录中的这些文件则是从 bluestore 盘一开始的 `BDEV_LABEL_BLOCK_SIZE=4096` 位置读取过来的。通过 以下命令，可以把所有的 label 打印出来

```
$ ceph-bluestore-tool  show-label --path /var/lib/ceph/osd/ceph-0
inferring bluefs devices from bluestore path
{
    "/var/lib/ceph/osd/ceph-0/block": {
        "osd_uuid": "2a464466-e5f8-48c8-ae26-b26e12b887cc",
        "size": 19323158528,
        "btime": "2020-04-12 03:05:20.158229",
        "description": "main",
        "bluefs": "1",
        "ceph_fsid": "63050303-aeab-45e9-9ad5-da01ea3b6851",
        "kv_backend": "rocksdb",
        "magic": "ceph osd volume v026",
        "mkfs_done": "yes",
        "osd_key": "AQBthZJebBpGOxAA+Y+uVPfzSXpr++2HiiRP3A==",
        "ready": "ready",
        "require_osd_release": "12",
        "whoami": "0"
    },
    "/var/lib/ceph/osd/ceph-0/block.wal": {
        "osd_uuid": "2a464466-e5f8-48c8-ae26-b26e12b887cc",
        "size": 1073741824,
        "btime": "2020-04-12 03:05:20.172686",
        "description": "bluefs wal"
    },
    "/var/lib/ceph/osd/ceph-0/block.db": {
        "osd_uuid": "2a464466-e5f8-48c8-ae26-b26e12b887cc",
        "size": 1073741824,
        "btime": "2020-04-12 03:05:20.164547",
        "description": "bluefs db"
    }
}
```

相关代码参看

- [ceph-volume activate](https://github.com/ceph/ceph/blob/d65b8844d16d71df01b57f368badc100db505506/src/ceph-volume/ceph_volume/devices/lvm/activate.py#L144)
- [ceph-bluestore-tool prime-osd-dir](https://github.com/ceph/ceph/blob/d65b8844d16d71df01b57f368badc100db505506/src/os/bluestore/bluestore_tool.cc#L316-L396)

使用ceph-volume， 不管 store 使用的是 filestore 还是 bluestore, 都会把一些 tag 存在 lvm 上面， 可以使用以下命令查看(做了格式化处理)

```console
$ lvs -o lv_tags ceph-20861703-1a01-415c-97c3-7e855cfb8994
ceph.block_device=/dev/ceph-20861703-1a01-415c-97c3-7e855cfb8994/osd.block
ceph.block_uuid=tXAc95-eeqZ-rBuv-r25S-UX22-iNyN-ts9Mkc
ceph.cephx_lockbox_secret=
ceph.cluster_fsid=63050303-aeab-45e9-9ad5-da01ea3b6851
ceph.cluster_name=ceph
ceph.crush_device_class=None
ceph.db_device=/dev/ceph-20861703-1a01-415c-97c3-7e855cfb8994/osd.db
ceph.db_uuid=1ced0p-o0kk-Vx32-VUAQ-PlM1-pRpX-e3SXnm
ceph.encrypted=0
ceph.osd_fsid=2a464466-e5f8-48c8-ae26-b26e12b887cc
ceph.osd_id=0
ceph.type=block
ceph.vdo=0
ceph.wal_device=/dev/ceph-20861703-1a01-415c-97c3-7e855cfb8994/osd.wal
ceph.wal_uuid=vqTGDo-szoS-9DeJ-yDwt-OmuB-OG2N-r5SzvW

ceph.block_device=/dev/ceph-20861703-1a01-415c-97c3-7e855cfb8994/osd.block
ceph.block_uuid=tXAc95-eeqZ-rBuv-r25S-UX22-iNyN-ts9Mkc
ceph.cephx_lockbox_secret=
ceph.cluster_fsid=63050303-aeab-45e9-9ad5-da01ea3b6851
ceph.cluster_name=ceph
ceph.crush_device_class=None
ceph.db_device=/dev/ceph-20861703-1a01-415c-97c3-7e855cfb8994/osd.db
ceph.db_uuid=1ced0p-o0kk-Vx32-VUAQ-PlM1-pRpX-e3SXnm
ceph.encrypted=0
ceph.osd_fsid=2a464466-e5f8-48c8-ae26-b26e12b887cc
ceph.osd_id=0
ceph.type=db
ceph.vdo=0
ceph.wal_device=/dev/ceph-20861703-1a01-415c-97c3-7e855cfb8994/osd.wal
ceph.wal_uuid=vqTGDo-szoS-9DeJ-yDwt-OmuB-OG2N-r5SzvW

ceph.block_device=/dev/ceph-20861703-1a01-415c-97c3-7e855cfb8994/osd.block
ceph.block_uuid=tXAc95-eeqZ-rBuv-r25S-UX22-iNyN-ts9Mkc
ceph.cephx_lockbox_secret=
ceph.cluster_fsid=63050303-aeab-45e9-9ad5-da01ea3b6851
ceph.cluster_name=ceph
ceph.crush_device_class=None
ceph.encrypted=0
ceph.osd_fsid=2a464466-e5f8-48c8-ae26-b26e12b887cc
ceph.osd_id=0
ceph.type=wal
ceph.vdo=0
ceph.wal_device=/dev/ceph-20861703-1a01-415c-97c3-7e855cfb8994/osd.wal
ceph.wal_uuid=vqTGDo-szoS-9DeJ-yDwt-OmuB-OG2N-r5SzvW
```

## osd 的盘是如何挂载的

ceph 依赖 systemd 来管理挂载，不需要配置 `/etc/fstab` 文件。在初始化 osd 的时候, ceph 会 enable 一个 ceph-volume@x.service 服务，其中 x 的格式如 `{lvm|simple}-{osd id}-{osd uuid}`, 这个服务会在系统的`local-fs.target` 组里面，当系统挂载本地盘的时候，会自动挂载上。

这个 ceph-volume@.service 定义如下

```console
$ systemctl cat ceph-volume@lvm-0-b7b4fa98-d36e-430b-9789-a432a078292c
# /usr/lib/systemd/system/ceph-volume@.service
[Unit]
Description=Ceph Volume activation: %i
After=local-fs.target
Wants=local-fs.target

[Service]
Type=oneshot
KillMode=none
Environment=CEPH_VOLUME_TIMEOUT=10000
ExecStart=/bin/sh -c 'timeout $CEPH_VOLUME_TIMEOUT /usr/sbin/ceph-volume-systemd %i'
TimeoutSec=0
[Install]
WantedBy=multi-user.target
```

可以看到， 他是把参数传递给了 `ceph-volume-systemd` 命令， 而这个命令又把参数解析后，传给了 `ceph-volume` 命令，最后的执行的命令是

```console
$ ceph-volume lvm trigger {osd id} {osd uuid]
```

> 需要`ceph-volume-systemd` 这个命令的原因应该是systemd只能传一个参数

这个 `trigger` 会调用 `ceph-volume lvm activate` 命令，去准备相对应挂载及里面的数据初始化。

最后， `ceph-volume lvm activate` 会调用 `ceph-bluestore-tool pirme-osd-dir` 命令来初始化里面的数据。

## 其它

### ceph osd purge

ceph Limunous 新加了一个 `ceph osd purge` 命令，很好用，可以一个命令，把某个 osd 相关的信息都清除掉。包括

- osd
- crush rule
- auth key

### ceph-disk lvm

ceph-disk 应试不支持 lvm 的， 参见 http://tracker.ceph.com/issues/5461

不过 kolla 是否支持，可以验证下， 因为 kolla 的脚本里面不依赖 ceph-disk

## 参考文章


* [ceph存储引擎bluestore解析](http://www.sysnote.org/2016/08/19/ceph-bluestore/)
* [new luminous bluestore](https://ceph.com/community/new-luminous-bluestore/)
* [ceph bluestore 基本原理](http://liyichao.github.io/posts/ceph-bluestore-%E5%9F%BA%E6%9C%AC%E5%8E%9F%E7%90%86.html)

## 版本

时间       | 更新内容
---------- | ------------------------
2018-04-07 | 初版
2018-11-25 | 增加 block.db 推荐大小值
2020-04-12 | 增加 block.db / block.wal 的配置

