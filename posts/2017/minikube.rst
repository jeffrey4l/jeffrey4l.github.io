使用 minikube 搭建 kubernetes 单机环境
######################################

:date: 2017.12.11
:tags: Docker, Kubernetes
:slug: minikube
:category: Container

minikube 可以快速搭建 kubernetes 单机环境，方便开发及测试使用。其支持大部分kubernetes的功能，列表如下

* DNS
* NodePorts
* ConfigMaps and Secrets
* Dashboards
* Container Runtime: Docker, and rkt
* Enabling CNI (Container Network Interface)
* Ingress

0x01 原理
=========

minikube 会下载一个 iso，并启动一台 virtualbox 虚拟机。把 kubernetes 在虚拟机里面跑起来。所以 minikube 可以在 windows 上运行。

0x02 安装
=========

由于某些原因，kubernetes 上面的资源可能下载不下来，最好你有一个好用的 VPN 或者 http 代理。

下载 minikube 工具

.. code-block:: console

    $ curl -L https://github.com/kubernetes/minikube/releases/download/v0.24.1/minikube-linux-amd64 \
        -o /usr/local/bin/minikube
    $ chmod +x /usr/local/bin/minikube

minikube 默认是使用 virtualbox 来启动虚拟机。我在 Linux 上面习惯使用 KVM, 所以还需要单独下载 kvm 的驱动。值的一提的是现在有 kvm 及 kvm2 两个驱动，其中 kvm 已经废弃掉，推荐使用 kvm2。

下载 kvm2 驱动

.. code-block:: console

    $ curl -L https://storage.googleapis.com/minikube/releases/latest/docker-machine-driver-kvm2 \
        -o /usr/local/bin/docker-machine-driver-kvm2
    $ chmod +x /usr/local/bin/docker-machine-driver-kvm2

安装 kubectl 命令

.. code-block:: console

    $ export version=$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)
    $ curl -L https://storage.googleapis.com/kubernetes-release/release/$(version)/bin/linux/amd64/kubectl \
         -o /usr/local/bin/kubectl
    $ chomd +x /usr/local/bin/kubectl

0x03 启动 kubernetes
====================

使用 minikube 启动 kubernetes 很简单，就一条命令

.. code-block:: console

    $ minikube start --vm-driver kvm2

如果你的网络访问有问题，运行这个命令时，最好接着 VPN 或使用 http 代理，因为虚拟机里面会下载一些镜像。使用 http 代理可以使用如下命令行

.. code-block:: console

    $ export http_proxy=http://10.10.0.22:8185
    $ export https_proxy=http://10.10.0.22:8185
    $ minikube start --vm-driver kvm2 \
        --docker-env http_proxy=$http_proxy \
        --docker-env https_proxy=$https_proxy

如果没有问题，你会看到如下信息

.. code-block:: console

    $ minikube start --vm-driver kvm2
    Starting local Kubernetes v1.8.0 cluster...
    Starting VM...
    Getting VM IP address...
    Moving files into cluster...
    Setting up certs...
    Connecting to cluster...
    Setting up kubeconfig...
    Starting cluster components...
    Kubectl is now configured to use the cluster.
    Loading cached images from config file.

0x04 测试
=========

通过 minikube 打开dashboard

.. code-block:: console

    $ minikube dashboard

通过 kubectl 查看现有服务

.. code-block:: console

    $ kubectl --namespace kube-system get svc
    NAME                   TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)         AGE
    kube-dns               ClusterIP   10.96.0.10      <none>        53/UDP,53/TCP   27m
    kubernetes-dashboard   NodePort    10.97.208.124   <none>        80:30000/TCP    27m

创建一个新服务

.. code-block:: console

    $ kubectl run hello-minikube --image=gcr.io/google_containers/echoserver:1.4 --port=8080
    deployment "hello-minikube" created

    $ kubectl expose deployment hello-minikube --type=NodePort
    service "hello-minikube" exposed

访问新创建的服务。

.. code-block:: console

    $ kubectl get pod                                  
    NAME                              READY     STATUS    RESTARTS   AGE
    hello-minikube-57889c865c-8fpq9   1/1       Running   0          13m

    $ curl $(minikube service hello-minikube --url)
    CLIENT VALUES:
    client_address=172.17.0.1
    command=GET
    real path=/
    query=nil
    request_version=1.1
    request_uri=http://192.168.39.136:8080/

    SERVER VALUES:
    server_version=nginx: 1.10.0 - lua: 10001

    HEADERS RECEIVED:
    accept=*/*
    host=192.168.39.136:32619
    user-agent=curl/7.57.0
    BODY:
    -no body in request-% 

删除服务

.. code-block:: console

    $ kubectl delete deployment hello-minikube
    deployment "hello-minikube" deleted

0x05 删除 kubernetes 集群
=========================

.. code-block:: console

    $ minikube stop

0x06 REF
========

* https://github.com/kubernetes/minikube/releases
* https://kubernetes.io/docs/getting-started-guides/minikube/
