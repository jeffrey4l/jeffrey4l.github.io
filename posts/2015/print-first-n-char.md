Title: Print the First N Characters of each Line
Date: 2015-2-15
Category: Linux
tags: Shell

在使用 Shell 的过程中，经常会遇到一行过长，导致输出折行，相当难看的情况出现。而且多数据情况下，我们只用每行的前 N 个字符就可以了。这时可以用以下方法来截断每行的长度。

**方法1**： 使用 `awk`

```
cat filename | awk '{print substr($0, 0, 20)}'
```


**方法2**: 使用 `sed`

```
cat filename | sed 's/\(.\{20\}\).*/\1/'
```

** 方法3**: 使用 `sed -r`

```
cat filename | sed -r 's/(.{20}).*/\1/'
```
