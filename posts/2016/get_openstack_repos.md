Title: Get all the repo from OpenStack
Date: 2016-1-6
Slug: get-all-repos-from-openstack
Category: OpenStack
Tags: OpenStach Python

OpenStack的源因为你我都知道的原因，一直不稳定，导致 devstack 时经常失败。特定写了个脚本，可以拿到所有的仓库地址，方便做本地的mirror。

脚本在 gist[^1] 上。

使用方法：

```
pip install PyGithub
python openstack_repo.py -u <github_username> -p <github_password> \
    -o repos.txt
```

跑一次才发现，OpenStack 组下已经有了600多个项目。好多啊。

[gist:id=b6c36b9f74b743eb4c82,file=openstack_repos.py]

[^1]: https://gist.github.com/jeffrey4l/b6c36b9f74b743eb4c82
