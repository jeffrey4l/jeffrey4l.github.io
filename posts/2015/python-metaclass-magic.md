Title: Python MetaClass Magic
Tags: Python
Date: 2015-5-18
Category: Python


在 Nova 代码中[[0](https://github.com/openstack/nova/blob/c13f693d496f4ea5dbc78244fefd9ec2d6ea8de5/nova/api/openstack/wsgi.py#L1075)]发现一个神奇的应用，利用 decrator 来区分同名的函数，根据 decrator 上面定义的版本，来调用不同的方法。仔细学习了一下。它是用到了 MetaClass。主要思路是：

* 在 decrator 里面，把被装饰的方法存在类的一个属性里面(version_methods)
* 使用自定义的metaclass, 删除掉父类上的version_methods，并把这个属性放到子类中。这样做是为了防止子类共享父类的version_methods属性。
* 在子类里面，重写`__getattribute__`方法，当所需要的属性存在于`version_methods`时，根据特定的条件，返回期望的方法。如果没有，就调用父类的方法。

以下是示例代码

[gist:id=0b974aaea1be25cde67d,file=version_method.py]


* [0] <https://github.com/openstack/nova/blob/c13f693d496f4ea5dbc78244fefd9ec2d6ea8de5/nova/api/openstack/wsgi.py#L1075>
