Title: PIP install from local
Date: 2015-1-8
Tags: Python
Category: Programming

在一些特殊环境中，服务器是不能联网的。此时要通过pip安装包会有一些麻烦。这时可以使用pip的download到本地的功能，来加速安装。

先在有网络的环境中下载下来所有需要的包：

```
pip install --download ${HOME}/.pip-packages -r requirement.txt
```

在把这些包拷贝到目标环境中去，使用下面的命令来安装：

```
pip install --no-index --find-links ${HOME}/.pip-packages -r requirement.txt
```

所有需要的包就安装上了。

为了方便使用，还可以把这两个命令弄成alias来使用

```
alias pipcache='pip install --download ${HOME}/.pip-packages'
alias pipinstall='pip install --no-index --find-links=file://${HOME}/.pip-packages/'
```
