Title: Deploy Docker Registry Service
Date: 2015-12-15
Category: Docker
Tags: Docker

使用 Docker 时，很多情况下需要搭建自己的 registry 服务。把一些私有的 Image 放到上面用。官方有一个 registry 的[镜像](https://hub.docker.com/_/registry/)可以拉下来，直接用。如下：

```
docker run -p 5000:5000 -v <HOST_DIR>:/tmp/registry-dev registry
```

但是默认没有加上 ssl(如果没有，只能给本机提供服务)， proxy也没有开启。

我自己写了一个 docker compose, 默认开启了以上两个功能，代码见[这里](https://github.com/jeffrey4l/docker-registry)。默认使用了 host 的 /data/docker-registry/data 目录做数据 volume, 所以请保证这个目录存在。

使用自己建立的 registry 服务时，要修改 docker 的服务启动脚本，加上如下参数：

```
--insecure-registry your.domain.com:5000 --registry-mirror=https://your.doamin.com:5000
```

# REF
* https://github.com/jeffrey4l/docker-registry
* https://github.com/docker/distribution/blob/master/docs/mirror.md
* https://hub.docker.com/_/registry/
