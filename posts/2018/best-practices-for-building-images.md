---
title: 制作镜像的最佳实践
date: 2018-10-03
status: draft
slug: best-practices-for-building-docker-images
---

## 构建体积更小的镜像

构建体积更小的镜像，有利于镜像本身的传输，尤其在 Kubernetes 的环境中，镜像的传输会更加频繁，更小的体积意味着更快的调度时间和更小的空间占用。那如何构建更加小的镜像呢?

### 使用更小的基础镜像

不同的基础镜像构建相同的应用会有不同的大小。使用更小基础镜像会有利于减小最终镜像的大小。建议非特殊情况下，使用 alpine 镜像。他的基础镜像只有不到 5MB, 而且还自带包管理工具。一般需求都可以满足。

```
FROM alpine
RUN apk add nginx
```

如果你的应用可以独立运行，如 Go 编译出来的 Binary 文件，还可以直接使用 scratch 这个空白镜像。

```
FROM scratch
COPY mybinary /mybinary
CMD [ "/mybinary" ]
```

### 合并 RUN 命令

不同的 RUN 命令如果先后做了文件的增加和删除，因为镜像分层文件系统的原因，还是会增加镜像体积的。如果两个 RUN 命令合并后，才会达到所想的效果。

```
...
RUN curl http://xyz.abc -o abc.tar.gz \
    ...
    rm -rf abc.tar.gz
...
```

### 去除掉不用的软件包

在安装包的过程中，尽量只安装需要用到的包。尤其是在编译过程中，难免会安装一些运行过程中不需要的软件包，如 glibc-devel 等。那在最后，最好把这些包去掉，来节省镜像空间。又因为镜像分层系统的原因，这些安装和卸载的语法还应该处理同一个 RUN 命令下

```
...
RUN BUILD_DEP_PKGS="
       gcc \
       libc-devel"
    && yum -y install $BUILD_DEP_PKGS \
    ...
    && yum -y remove $BUILD_DEP_PKGS
...
```

### 只安装必要依赖包的

`apt` 和 `yum/dnf` 在安装包的过程中，默认会自动安装一些弱依赖包。一般情况下是使用不到的。可以显示的关闭弱依赖。

```
# apt-get for Debian family
apt-get -y install --no-install-recommends {{ package }} 

# yum from RHEL family
yum -y --setopt=install_weak_deps=false \
    --setopt=tsflags=nodocs \
    --setopt=override_install_langs=en_US.utf8 \
    install vim
```

* `--no-install-recommends` : 不安装推荐依赖
* `--setopt=install_weak_deps=false`: 不安装弱依赖包
* `--setopt=tsflags=nodocs`: 不安装文档包
* `--setopt=override_install_langs=en_US.utf8`: 设置默认语言为 `en_US.utf8`

###  关闭用户初始化 lastlog 和 faillog 数据库

如果你要在镜像中创建新的用户，可以不初始化用户相关的 lastlog 和  faillog 数据库[1]。可以使用 `useradd -l` 或把 `/var/log/faillog` 和 `/var/log/lastlog` 文件删除掉，彻底关掉该功能。每个用户大概用占用掉 4k 左右的空间。

### 使用 multi stage 构建

对于很多需要编译运行的程序，如 Java, C, Golang 等，其编译环境和运行环境是不一样的，为了减小最终镜像的大小，我们可以使用上面提到的合并 `RUN` 命令的方式，但是看着会比较乱，比较难以维护。docker daemon >= 17.05 [^3]版本的时候支持 multi stage 构建，解决了此类问题，他使用两个镜像来构建，通过 `COPY --from` 语法，在两个镜像之间传递构建好的文件。使用方法如下：

```dockerfile
FROM golang:1.7.3 as builder
WORKDIR /go/src/github.com/alexellis/href-counter/
RUN go get -d -v golang.org/x/net/html  
COPY app.go    .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

FROM alpine:latest  
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /go/src/github.com/alexellis/href-counter/app .
CMD ["./app"]  
```

它使用 `golang:1.7.3` 做为构建镜像，来构建出名为 `app` 的应用，然后把  `app` 再拷贝到以 `alpine:latest` 为基础的镜像里面，这样做出来的镜像肯定会很小。

## 缩小镜

## 像体积

### 使用 dive 分析镜像的空间占用

[dive](https://github.com/wagoodman/dive) 是一个命令行工具，可以分析镜像里面每层的空间占用大小，有助于发现问题，以减少镜像大小。

![dive example](images/2018/dive-demo.gif)

### 合并镜像的多个层

docker 自从 1.13 版本增加了一个 squash 的 `experimental`特性 [^2]。他可以把把当前 Dockerfile 文件里面的多个层在构建的时候自动合并成一个。但是不支持合并其父镜像。使用前，需要打开 docker daemon 的 experiment 特性。使用方法如下

```
$ docker build --squash .
```
除了这个方法，还有一个工具叫 [docker squash](https://github.com/goldmann/docker-squash) ， 他支持合并镜像的任意层。使用方法如下
```
$ pip install docker-squash
$ docker-squash -t kolla/centos-source-base:new \
      kolla/centos-source-base:master
Old image has 40 layers
Attempting to squash last 40 layers...
...
Original image size: 388.51 MB
Squashed image size: 281.43 MB
Image size decreased by 27.56 %
Image registered in Docker daemon as kolla/centos-source-base:new
```

可以看到，通过 `squash` 镜像大小从 `388.51MB` 缩小到了 `281.43MB` ，缩小了 `27.56%` 。

> 注意：在使用 squash 的时候，会消耗大量的硬盘 IO，如果硬盘性能不好，速度会比较慢。

##  镜像安全

### init 进程

重启容器的时候，经常会很慢，而且docker daemon 日志中经常会抛出以下错误

```
dockerd[559]: msg="Container 5054f failed to exit within 10 seconds of signal 15 - using the force"
```

默认的的 signal 15 根本就没有使其退出，最后还是 10 秒超时后强制退出(kill)的。而且有时还会出现大量僵尸进程。

容器化后，由于单容器单进程，已经没有传统意义上的 init 进程。应用进程直接占用了 pid 1 的进程号，应用默认是不会处理`SIGTERM` 信号的，所以会导致 signal 15 不能使进程正常退出，只能使用 `SIGKILL` 直接杀死进程。而这可能导致某些资源不能正常回收。另外 pid 1 进程还需要负责其子进程的回收工作，但是一般应用也不会对此进行处理。所以会导致僵尸进程的出现。更多解释，请参看我写的另外一篇文章：[Docker init 进程](docker-init-process)

解决方案是使用 [tini]( https://github.com/krallin/tini) , 或 [dumb-init](ttps://github.com/Yelp/dumb-init) 等轻量级 init 进程。所以在制作镜像的时候最好安装上其中一个。

```dockerfile
# install dumb-init
RUN wget -O /usr/local/bin/dumb-init \
    https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64
RUN chmod +x /usr/local/bin/dumb-init

# Runs "/usr/bin/dumb-init -- /my/script --with --args"
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/my/script", "--with", "--args"]
```

如果是使用 docker 的情况下，docker 自 1.13 之后已经自带一个 init 进程，其实就是  tini, 使用方法如下

```
$ docker run --init centos:7 ps auxf
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0   1000     4 ?        Ss   03:45   0:00 /dev/init -- ps auxf
root         6  0.0  0.0  51748  3444 ?        R    03:45   0:00 ps auxf
```

### Drop root

虽然 container 在运行的时候 ，是与系统隔离开的，但是如果你使用 root 运行容器的话，他在系统层面上看，也是 root 账号，权限是比较大的，[会有一定的风险](https://security.stackexchange.com/questions/176206/docker-runs-container-processes-as-root-should-i-be-worried)。更安全的做法是使用非root 账号运行。这点在 openshift 上面体现的比较明显，他默认是使用一个很大的 uid 来运行，来限制容器内的进程权限。

在使用非 root 账号运行，尤其是在 kubernetes/openshift 这种环境中，uid 是不能事先确认的，需要对读写目录标记上`0777` 的权限。包括某些可能通过  volume 挂载的目录。

> 注意，对于 volume 挂载的目录，在 kubernetes/openshift 环境中，并不是必要的，volume 目录的 uid / gid 会由 kubelet 自动配置好。

例子如下

```dockerfile
RUN ... \
    && rm -rf /etc/nginx/*.default \
    && chmod -R a+rwx ${NGINX_HOME_TMP} \
    && chmod -R a+rwx /etc/nginx \
    && chmod -R a+rwx /var/log/nginx \
    && chmod -R a+rwx /var/run/nginx
```

把需要  nginx 读写的地方配置上  `rwx` 权限，这样不管 nginx 进程的 `uid`  是多少，都可以正常运行。

## 镜像 tag 管理 

理论上讲，docker 的镜像内容是不可变的，其 tag 应该是和 git 的 tag 是一样的，应该是一个只读值不应该变化。但是平时大家在使用的时候，习惯的使用 `:latest` ， 这样在生产环境中是比较危险的，很容易搞错镜像。我建议使用如下风格的 tag 命令方式来管理 image.

```
X.Y.Z-N

X.Y.Z 跟随镜像里面关联代码的版本号
N 使用构建次数，或使用时间戳。来标记 Dockerfile 的变化及构建时间
```

## 其它镜像构建方式

现在，除了 `Dockerfile` 这种构建方式，还有很多其它的镜像构建工具，有兴趣可以深入研究下

* [source to image](https://github.com/openshift/source-to-image): openshift 里面带的一个方便由源代码直接生成镜像的方案，可以单独使用。
* [makisu](https://github.com/uber/makisu): 方便在  kubernetes 环境中使用的镜像构建方案，可以 unprivileged 的容器中使用
* [buildash](https://github.com/containers/buildah): 构建 OCI 兼容格式镜像工具。

## Demo

```
FROM centos:7

EXPOSE 8080
EXPOSE 8443

ARG http_proxy
ARG https_proxy

ARG NGINX_MODULE_VTS_VERSION=v0.1.18
ARG NGINX_VERSION=1.13.3
ARG TINI_VERSION=v0.18.0

ENV NGINX_GROUP nginx
ENV NGINX_HOME_TMP /var/spool/nginx/tmp
ENV NGINX_HOME /var/lib/nginx
ENV NGINX_USER nginx

ENV NGINX_DOWNLOAD_URL http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz

RUN BUILD_DEP_PKGS="\
        cpp \
        expat-devel \
        fontconfig-devel \
        freetype-devel \
        gcc \
        gd-devel \
        git \
        glibc-devel \
        glibc-headers \
        kernel-headers \
        keyutils-libs-devel \
        krb5-devel \
        libcom_err-devel \
        libjpeg-turbo-devel \
        libpng-devel \
        libselinux-devel \
        libsepol-devel \
        libverto-devel \
        libX11-devel \
        libXau-devel \
        libxcb-devel \
        libxcb-devel \
        libXpm-devel \
        make \
        openssl-devel \
        pcre-devel \
        xorg-x11-proto-devel \
        zlib-devel \
        " \
    && rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7 \
    && yum -y --setopt=install_weak_deps=false --setopt=tsflags=nodocs --setopt=override_install_langs=en_US.utf8 \
        install \
        ${BUILD_DEP_PKGS} \
        rsync \
        wget \
    && curl -L https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini -o /tini \
    && chmod +x /tini \
    && wget ${NGINX_DOWNLOAD_URL} -O /tmp/nginx.tar.gz \
    && tar xf /tmp/nginx.tar.gz -C /tmp \
    && git clone --branch ${NGINX_MODULE_VTS_VERSION} https://github.com/vozlt/nginx-module-vts.git /tmp/nginx-module-vts \
    && ( \
        cd /tmp/nginx-${NGINX_VERSION} \
        && ./configure \
                --add-module=/tmp/nginx-module-vts \
                --conf-path=/etc/nginx/nginx.conf \
                --error-log-path=/var/log/nginx/error.log \
                --group=${NGINX_GROUP} \
                --http-client-body-temp-path=${NGINX_HOME_TMP}/client_body \
                --http-fastcgi-temp-path=${NGINX_HOME_TMP}/fastcgi \
                --http-log-path=/var/log/nginx/access.log \
                --http-proxy-temp-path=${NGINX_HOME_TMP}/proxy \
                --http-uwsgi-temp-path=${NGINX_HOME_TMP}/uwsgi \
                --lock-path=/var/local/subsys/nginx \
                --modules-path=/usr/lib64/nginx/modules \
                --pid-path=/var/run/nginx/nginx.pid \
                --prefix=/etc/nginx \
                --sbin-path=/usr/bin/nginx \
                --user=${NGINX_USER} \
                --with-http_gzip_static_module \
                --with-http_image_filter_module \
                --with-http_realip_module \
                --with-http_secure_link_module \
                --with-http_ssl_module \
                --with-http_stub_status_module \
                --with-http_sub_module \
                --with-http_v2_module \
                --without-http_scgi_module \
                --without-mail_imap_module \
                --without-mail_pop3_module \
                --without-mail_smtp_module \
                --without-poll_module \
                --without-select_module \
                --with-threads \
        && make -j4 \
        && make install \
        && cp -r conf/* /etc/nginx/ \
        ) \
    && rm -rf /tmp/nginx.tar.gz \
        /tmp/nginx-module-vts \
        /tmp/nginx-${NGINX_VERSION} \
    && yum -y remove ${BUILD_DEP_PKGS} \
    && yum clean all \
    && mkdir -p ${NGINX_HOME_TMP}/{client_body,proxy,fastcgi,uwsgi} \
    && mkdir -p /usr/share/nginx \
    && mkdir -p /var/run/nginx \
    && mkdir -p /var/www \
    && mv /etc/nginx/html /usr/share/nginx/ \
    && rm -rf /etc/nginx/*.default \
    && chmod -R a+rwx ${NGINX_HOME_TMP} \
    && chmod -R a+rwx /etc/nginx \
    && chmod -R a+rwx /var/log/nginx \
    && chmod -R a+rwx /var/run/nginx \
    && sed -i '/listen/s,listen\s*80;,listen 8080;,g' /etc/nginx/nginx.conf \
    && sed -i '/^#user/s,#\(user.*\),\1,g' /etc/nginx/nginx.conf \
    && ln -sf /var/log/nginx /etc/nginx/logs \
    && ln -sf /var/www /etc/nginx/www
```

## REF

* [^1]: https://github.com/sagemathinc/cocalc/issues/2287#issue-249824529
* [^2]: https://docs.docker.com/engine/reference/commandline/build/#squash-an-images-layers---squash-experimental
* [^3]: <https://docs.docker.com/develop/develop-images/multistage-build/> 
* [^4]: [10 tips for building and managing containers](https://www.weave.works/blog/10-tips-for-building-and-managing-containers)
