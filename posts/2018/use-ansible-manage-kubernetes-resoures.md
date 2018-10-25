title: 使用 Ansible 管理 Kubernetes 资源
date: 2018-10-22
slug: use-ansible-manage-kubernetes-resources

前两天，一篇[「Think twice before using Helm」](https://medium.com/virtuslab/think-twice-before-using-helm-25fbb18bc822)(译文:[「恕我直言，对Helm大家还是要三思而后用」](https://mp.weixin.qq.com/s/5iG9kZl7Qp5l3_BCXajrSA)) 引起了大家的关注。作者从认证，生命周期管理，错误处理等多个角度说明了 Helm 自身的问题。我基本赞同作者的观点。多数情况下我们只是把 helm 当做一个模板引擎在使用，把 charts 生成 Kubernetes 可以处理的格式。但是从使用角度来说，这个模板实现的太重了。有兴趣的可以去读读原文。

那如果 Helm 不轻量好用的话，我们有啥其他选择?

Ansible 做为部署管理的工具，正在受到越来越多的运维人员的追捧。他支持 Jinja2 的模板引擎，而且是无代理节点的架构，很方便来做一些模板工作。所以本文来介绍使用 Ansible 如何管理 Kubernetes 上面的资源。

首先使用 Ansible 避免不了使用其模块。与 Kubernetes 相关的模块可以从[1]找到。现在主要有`k8s`, `k8s_facts`, `k8s_scale`, `kubernetes`和`oc` 5个模块。其中 `kubernetes` 和 `oc` 模块因为实现逻辑不好用，在 ansible 2.6 版本中已经废弃掉， 推荐使用前三个。其中，`k8s_scale` 来自 ansible 2.5, `k8s` 来自 ansible 2.6, `k8s_facts` 来自 ansible 2.7。使用这三个模块的话，还需要安装 `openshift` 的 Python 包。以下代码全部基于 ansible 2.7 版本。

## k8s 模块

管理 kubernetes 各种资源的话，使用 `k8s` 模块就可以了，如下是创建 namespace 的写法

```yaml
- name: Create a k8s namespace
  k8s:
    name: testing
    api_version: v1
    kind: Namespace
    state: present
```

如果要创建一个 Service, 也可以使用如下面的写法。

```YAML
- name: Create a Service object from an inline definition
  k8s:
    state: present
    definition:
      apiVersion: v1
      kind: Service
      metadata:
        name: web
        namespace: testing
        labels:
          app: galaxy
          service: web
      spec:
        selector:
          app: galaxy
          service: web
        ports:
          - protocol: TCP
            targetPort: 8000
            name: port-8000-tcp
            port: 8000
```

可以看到 `definition` 里面就是原生的 Kubernetes 里面的写法，而 `k8s` 模块的参数也写少，所以上手会很快。

如果 k8s 模块和 ansible `lookup` 插件合用的话，可以写出更加简洁的代码，如下

```
# tasks.yml
- name: Create a Service object from an external file
  var:
    name: "web"
  k8s:
    state: present
    definition: "{{ lookup('template', '/path/to/service.yml') | from_yaml }}"
```

```
# /path/to/service.yml
---
apiVersion: v1
kind: Service
metadata:
  name: {{ name }}          # <-- 这里可以使用变量
namespace: testing
labels:
  app: galaxy
  service: web
spec:
  selector:
    app: galaxy
    service: web
ports:
  - protocol: TCP
    targetPort: 8000
    name: port-8000-tcp
    port: 8000
```

可以看到 Kubernetes service 文件可以完全从 task 里面独立出来，独立后的写法就是原生的 kubernetes 的格式，基本就和 Charts 的结构差不多了。

基于此，完全可以使用这种方式替换掉 helm 的模板功能，而且没有引入任何额外的依赖，就是直接的 ansible 生成相关文件，丢给 kubernetes api 来处理。等部署完成后，我们也可以脱离 Ansible 继续通过 `kubelet` 命令维护这些资源。也正是由于这么简洁的实现，`k8s` 模块可以管理 Kubernetes 和 OpenShift, 也可以管理各种 `CRD` 资源。

相比于 helm ， 这种方法的缺点在于 YAML 文件都要自己写，没有社区在维护的 Charts。不像 helm 那样，一个命令就可以把服务都安装上。前期的工作还是挺多的。但是从另外一个角度来说，社区维护的 Charts 做一些 Demo 还可以，真要生产上面使用，还是要做大量工作的。所以从这个角度上讲，使用 Ansible 也没有带来太大的工作量。

我更期待社区可以使用 Ansible 直接管理 Charts 资源，或可以有一个工具把 Charts 的 Go 模板转成 Ansible 可以接受的 Jinja2 格式。

## k8s_scale 和  k8s_facts 模块

这两个模块算辅助的功能，我觉得使用的机会可能并不会太多。`k8s_scale` 的例子如下

```
- name: Scale deployment up, and extend timeout
  k8s_scale:
    api_version: v1
    kind: Deployment
    name: elastic
    namespace: myproject
    replicas: 3
    wait_timeout: 60

- name: Scale deployment down when current replicas match
  k8s_scale:
    api_version: v1
    kind: Deployment
    name: elastic
    namespace: myproject
    current_replicas: 3
    replicas: 2
```

它可以动态调整 Deployment 的 `replicas` 个数，基本上等同于`kubectl scale` 命令，但是这个功能基本可以使用 `k8s` 模块通过改变 `replicas` 参数来调整。

`k8s_facts`的例子如下

```
- name: Get an existing Service object
  k8s_facts:
    api_version: v1
    kind: Service
    name: web
    namespace: testing
  register: web_service
```

使用他，你可以检查某个资源是否存在，如果存在的话，还可以获得这个资源的yaml 文件描述，我觉得在 Ansible 流程控制中会有一些作用，可以根据当前 Kubernets 里面资源情况，有选择的做一些动作。

## 小技巧

因为 Ansible 是 Python 编写的，在使用 pip 安装时容易破坏系统已经安装的 Python 包，推荐使用虚拟环境来安装。

```
# mkvirtualenv --system-site-packages ansible
# pip install 'ansible<2.7' openshift
```

使用时，需要指定 Ansible 使用的 python interpreter 变量 

```
# workon ansible
# ansible-playbook -i localhost, -c local test.yml  -e ansible_python_interpreter=${VIRTUAL_ENV}/bin/python
```

## demo

以下是使用 ansible 在 OpenShift 上面部署 echoserver 的一个完整例子

```
---
- hosts: localhost
  connection: local
  gather_facts: false
  vars:
    namespace: demo
  tasks:
    - name: Create echo server deployment config
      k8s:
        namespace: "{{ namespace }}"
        definition:
          apiVersion: v1
          kind: DeploymentConfig
          metadata:
            name: echoserver
          spec:
            replicas: 1
            template:
              metadata:
                labels:
                  app: echoserver
              spec:
                containers:
                  - name: echoserver
                    image: googlecontainer/echoserver:1.5
                    readnessProbe:
                      httpGet:
                        port: 8080
                        path: /
                      initialDelaySeconds: 20
                      periodSeconds: 5
                    livenessProbe:
                      httpGet:
                        port: 8080
                        path: /
                      initialDelaySeconds: 10
                      periodSeconds: 3
    - name: Create echo server service
      k8s:
        namespace: "{{ namespace }}"
        definition:
          apiVersion: v1
          kind: Service
          metadata:
            name: echoserver
          spec:
            ports:
              - name: http
                port: 8080
                targetPort: 8080
            selector:
              app: echoserver
    - name: Create echo server router
      k8s:
        namespace: "{{ namespace }}"
        definition:
          kind: Route
          apiVersion: route.openshift.io/v1
          metadata:
            name: echoserver
          spec:
            host: echoserver.local
            to:
              kind: Service
              name: echoserver
            port:
              targetPort: http
```



* [1] <https://docs.ansible.com/ansible/latest/modules/list_of_clustering_modules.html>
