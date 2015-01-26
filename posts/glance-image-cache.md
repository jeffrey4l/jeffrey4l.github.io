Title: Glance Image Cache
Date: 2014-7-17
Tags: Glance
Category: OpenStack

Glance 增加了一层cache的Middleware，用来缓存从file store后端取过来的镜像。一定
程度上可以加快取镜像的速度。这个功能默认情况下是没开启的。

因为是通过middleware来控制的，所以只要修改一下paster的配置就行。更简单的是指定
glance-api加载的pipeline的名字。

```ini
[deploy]
# possible value: none, cachine, keystone, keystone+caching, 
# keystone+cachemanagement
# This value can get from glance-api-paste.conf file
flavor=keystone+caching
```

具体看下`glance-api-paster.conf`文件就能明白。
```ini
[pipeline:glance-api]
pipeline = versionnegotiation unauthenticated-context rootapp

# Use this pipeline for image caching and no auth
[pipeline:glance-api-caching]
pipeline = versionnegotiation unauthenticated-context cache rootapp

# Use this pipeline for caching w/ management interface but no auth
[pipeline:glance-api-cachemanagement]
pipeline = versionnegotiation unauthenticated-context cache cachemanage rootapp

# Use this pipeline for keystone auth
[pipeline:glance-api-keystone]
pipeline = versionnegotiation authtoken context rootapp

# Use this pipeline for keystone auth with image caching
[pipeline:glance-api-keystone+caching]
pipeline = versionnegotiation authtoken context cache rootapp

# Use this pipeline for keystone auth with caching and cache management
[pipeline:glance-api-keystone+cachemanagement]
pipeline = versionnegotiation authtoken context cache cachemanage rootapp
```

不同的pipeline用到了不同的middleware, 启作用的是cache 和 cachemanagement这两个
。

## REF
1. [The Glance Image Cache](http://docs.openstack.org/developer/glance/cache.html)
