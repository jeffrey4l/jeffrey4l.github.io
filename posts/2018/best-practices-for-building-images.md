title: 制作镜像的最佳实践
date: 2018-10-03
status: draft
slug: best-practices-for-building-docker-images


* 选择合适的基础镜像
* 

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

###  关闭用户初始化 lastlog 和 faillog 数据库

如果你要在镜像中创建新的用户，可以不初始化用户相关的 lastlog 和  faillog 数据库[1]。可以使用 `useradd -l` 或把 `/var/log/faillog` 和 `/var/log/lastlog` 文件删除掉，彻底关掉该功能。每个用户大概用占用掉 4k 左右的空间。


## 使用 dive 分析镜像的空间占用

[dive](https://github.com/wagoodman/dive) 是一个命令行工具，可以分析镜像里面每层的空间占用大小，有助于发现问题，以减少镜像大小。

![dive example](images/2018/dive-demo.gif)

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

* [1] https://github.com/sagemathinc/cocalc/issues/2287#issue-249824529
