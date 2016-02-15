Title: Docker Mount Propagation
Date: 2016-02-07
Slug: docker_mount_propagation
Category: Linux
Tags: Docker, Mount

Docker 1.10 已发，官方 Release Note 在这里[^1]。其中最感觉最有用的其实是 Mount Propagation 功能，但是官方并没有对其进行介绍。本方来详解一下这个功能。

! 问题

老版本的 Docker 中有一个问题，Container A 中 Mount 后，其它 Container 里是看不到的。例如：

```
# container A
$ docker run --privileged -it -v data_vol:/mnt centos bash
[root@14df8f5f18ec /]# cd /mnt
[root@14df8f5f18ec mnt]# mkdir etc
[root@14df8f5f18ec mnt]# mount --bind /etc etc
[root@14df8f5f18ec mnt]# ls etc
...
BUILDTIME                centos-release-upstream
...

# container B
$ docker run -it --privileged -v data_vol:/mnt centos bash
[root@d54f50441927 mnt]# ll /mnt/etc
total 0
```

可以看出，在 Container A 是挂载的目录，在 Container B 中是看不到的。特殊情况下，会造成一些问题。比较多 Container 中共享 namespace 。Kolla 中的 neutron agents 就会有这个问题，所以 work around 就是把 l3,l2, dhcp 安装到同一个 container 里。

! Mount Propagation

解决方法就是使用 Linux Mount shared subtree 功能[^2]。具体功能介绍可以看这个链接[^2]。主要讲下 Docker 里面的使用。

!! 配置

Docker 需要修改下 systemd 的启动文件才可以使用 shared mount。

```
sed -i 's/MountFlags=.*/MountFlags=shared/g' /usr/lib/systemd/system/docker.service
```

修改后，文件如下：

```
[Unit]
Description=Docker Application Container Engine
Documentation=https://docs.docker.com
After=network.target docker.socket
Requires=docker.socket

[Service]
Type=notify
ExecStart=/usr/bin/docker daemon -H fd:// -g /home/docker --storage-driver overlay
MountFlags=slave
LimitNOFILE=1048576
LimitNPROC=1048576
LimitCORE=infinity
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

!! 测试

这个时候再进行上面的测试能成功了

```
# container A
$ docker run --privileged -it -v data_vol:/mnt centos bash
[root@14df8f5f18ec /]# cd /mnt
[root@14df8f5f18ec mnt]# mkdir etc
[root@14df8f5f18ec mnt]# mount --bind /etc etc
[root@14df8f5f18ec mnt]# ls etc
...
BUILDTIME                centos-release-upstream
...

# container B
$ docker run -it --privileged -v data_vol:/mnt centos bash
[root@d54f50441927 mnt]# ll /mnt/etc
total 0
```

! REF

[^1]: https://blog.docker.com/2016/02/docker-1-10/
[^2]: https://www.kernel.org/doc/Documentation/filesystems/sharedsubtree.txt
