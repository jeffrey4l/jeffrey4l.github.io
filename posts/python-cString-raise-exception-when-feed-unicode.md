Title: Python cString raise exception when feed Unicode
Date: 2014-9-9
Tags: python
Slug: python-cstring-unicode

I gett following different result when using these two Class.

```ipython
>>> import StringIO
>>> import cStringIO
>>> StringIO.StringIO().write(u'\u2222')
>>> cStringIO.StringIO().write(u'\u2222')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
UnicodeEncodeError: 'ascii' codec can't encode character u'\u2222' in position 0: ordinal not in range(128)
```

The root cause is explained on [document for cStringIO](https://docs.python.org/2/library/stringio.html#cStringIO.StringIO)

>Unlike the StringIO module, this module is not able to accept Unicode strings that cannot be encoded as plain ASCII strings.

