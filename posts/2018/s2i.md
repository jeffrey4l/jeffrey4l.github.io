title: Source to Image 工具介绍
date: 2018-01-16
tags: Docker, Container
category: Container
slug: s2i

## 介绍

Source to Image(S2I) 是一个创建 Docker 镜像的工具。也是 openshift 上面的主要构建镜像的方式之一。他的优点包括：

1. **速度**，S2I 可以实现很复杂的操作逻辑，而不会创建新的镜像层，所以运行起来很快。
2. **打补丁**，如果所依赖的镜像需要安全补丁，S2I 允许你一次性重新构建所有镜像。
3. **高效**, 在构建过程中，S2I不允许运行任意的 yum install 命令，以防止降低开发迭代速度 
4. **生态**，S2I 鼓励一个共享镜像生态。从而你的应用可以实现最佳实践。
    
## S2I 工作原理

S2I 的实现哲学是：所谓的镜像，就是一个运行环境 + 源代码。如是你是某一个类型的源代码，如果 Python, Ruby, HTML 等，那运行环境基本就是固定的。因此针对某类代码，只要提供好一个标准运行环境的基础镜像。使用的时候，先把用户的代码放到这个镜像中，生成一个新的镜像就可以。S2I 很适合给特定语言使用。

S2I 会依赖一个特殊的 base 镜像，这个镜像主要包括基础的运行环境，如 Python, PHP，Nginx等。以及几个特殊的 S2I 脚本， 如

- `assemble` 主要负责将你的源代码安装到这个特殊的镜像中
- `run` 主要指明你的源代码如何运行起来的
- `usage` 打印使用说明

redhat 官方有一些已经编写好的镜像例子[^2]，可以从找到。像 [Python](https://github.com/sclorg/s2i-python-container), [Ruby](https://github.com/sclorg/s2i-ruby-container)。利用这些镜像，再加上你的源代码，可以快速构建出应用镜像。

## 安装 S2I 工具

S2I 是一个 Go 编写的程序，你可以从 Github 上面下载已经编译的二进制文件[^1]，也可以自己编译。下面是手动编译的方法。

    ::console
	$ S2I_URL=github.com/openshift/source-to-image
	$ go get ${S2I_URL}
	$ cd ${GOPATH}/src/${S2I_URL}
    $ export PATH=$PATH:${GOPATH}/src/${S2I_URL}/_output/local/bin/linux/amd64/
    $ make all

## 使用 S2I 构建镜像

下面我们来使用 S2I 的功能，快速构建一个 Python 应用。

首先，先构建一个通用的 Python 2.7 基础镜像

    ::console
	$ git clone https://github.com/sclorg/s2i-python-container.git
    $ cd s2i-python-container/2.7
    
    $ docker build . -t local/s2i-python27
    
这一步操作，和普通的 Docker 镜像构建是一样的，并没有什么不同。通查看 `Dockerfile` 可以看到，

- Dockerfile 的父镜像是 `centos/s2i-base-centos7`[^4], 这是一个 CentOS 提供的 S2I 基础镜像。
- 这个镜像中安装了一样常用的 Python 软件包。
- 唯一特殊的是把 `./s2i/bin/` 目录拷贝到了 `STI_SCRIPTS_PATH` ( 也就是 `/usr/libexec/s2i` ) 位置。查看这个目录中的文件，就会看到上面提到的 `run`, `assemble` 及 `usage` 三个文件。
    
这样我们就得到了一个叫`local/s2i-python27:latest` 的基本镜像。下一步，把 Python 源代码打包入python 的基本镜像中。

    ::console
	$ cd test/django-test-app
    $ s2i build test/django-test-app  \
    	local/s2i-python27:latest \
        django-test-app:latest
    ---> Installing application source ...
    ---> Installing dependencies ...
    Collecting Django==1.8.1 (from -r requirements.txt (line 1))
    Downloading Django-1.8.1-py2.py3-none-any.whl (6.2MB)
    ...
    Build completed successfully

这个过程中，S2I 会做以下几个事情 

1. 利用 `local/s2i-python27:latest` 镜像启动一个临时容器
2. 把 `test/django-test-app` 代码放到容器里面的 `/tmp/src` 位置
    - 这里先把源代码转成tar包，再通过容器的 stdout 把 tar 文件传入容器中，并解压到 `/tmp/` 位置
3. 调用 `assemble` 脚本进行源代码的安装
4. 等 3 运行完成退出后，容器也就退出了
5. 容器退出后，把容器提交为一个镜像
    - `docker commit`
  
这时，一个名叫`django-test-app:latest`就构建好了，查看他的历史可以看到：

    ::console
	$ docker history django-test-app 
    IMAGE         CREATED BY                                      SIZE     
    c1775906f248  /bin/sh -c tar -C /tmp -xf - && /usr/libexec…   21.6MB
    df3a71bbe741  /bin/sh -c #(nop)  CMD ["/bin/sh" "-c" "$STI…   0B
    c699d75eb185  /bin/sh -c #(nop)  USER 1001                    0B   
    d3fa140aca9e  /bin/sh -c source scl_source enable python27…   18.4MB
	...
    
对比`centos/s2i-base-centos7`就会发现， 上面这个镜像只增加了一个层次。

最后直接启动镜像验证

    ::console
    $ docker run -it --rm django-test-app
    ---> Migrating database ...
    Operations to perform:
      Synchronize unmigrated apps: staticfiles, messages
      Apply all migrations: admin, contenttypes, auth, sessions
    Synchronizing apps without migrations:
      Creating tables...
        Running deferred SQL...
      Installing custom SQL...
    Running migrations:
      Rendering model states... DONE
      Applying contenttypes.0001_initial... OK
      Applying auth.0001_initial... OK
	...
    Django version 1.8.1, using settings 'project.settings'
    Starting development server at http://0.0.0.0:8080/
    Quit the server with CONTROL-C.

[^1]: <https://github.com/openshift/source-to-image/releases>
[^2]: <https://github.com/sclorg?q=s2i>
[^3]: <https://blog.openshift.com/create-s2i-builder-image/>
[^4]: <https://hub.docker.com/r/centos/s2i-base-centos7/>
[^5]: <https://github.com/openshift/source-to-image>
