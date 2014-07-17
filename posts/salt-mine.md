Title: Salt Mine
Date: 2014-7-16
Tags: salt
Category: Linux

Salt mine 可以在一定的控制内让minion拿到其它minion的信息。实现原理是：通过配置，让minion定期(最短为1分钟)的向master发送数据，而其它minion可以从master拿到这些数据。一定程度上实现的minion之间的通迅。在搭建cluster时，十分有用。

可以通过两种方法来配置:

1. minion的配置文件
2. master的pillar

使用minion配置时，要直接修改minion的配置文件，在`/etc/salt/minion.d/mine.conf` 加入如下内容

```yaml
mine_functions:
  test.ping: []
  network.ip_addrs:
    interface: eth0
```

使用pillar时配置时，只需要修改master的pillar配置即可。如在`/srv/pillar/mine.conf` 中加入如下内容

```yaml
mine_functions:
  test.ping: []
  network.ip_addrs:
    interface: eth0
```
然后把`mine.conf`加入到`/srv/pillar/top.sls`, 这时可以指定哪些minion来配置mine_functions。相比较而言，这种方式更加灵活一些。
```yaml
base:
  'controller*':
    - mine
```

之后就可以使用如下语句拿到mine上报上来的结果的(其实这个结果是保存在master的`/var/cache/salt/master/minions/*/mine.p`的文件下就可找到上报上来的内容。

```sh
$ salt 'jeffrey-thinkpad' mine.get '*' network.ip_addrs
jeffrey-thinkpad:
    ----------
    icehouse-compute:
        - 10.0.0.11
    icehouse-controller:
        - 10.0.0.10
```

另外，可以在minion上来修改上报的时间间隔。方法是增加/修改`/etc/salt/minion.d/mine.conf`。
```
mine_interval: 1
```


## REF
1. [Salt Mine](http://docs.saltstack.com/en/latest/topics/mine/)
