Title: 论Python的异常的合理抛出姿势
Slug: How_to_raise_python_exception
Date: 2015-5-6
Tags: Python, Exception
Category: Programming



当需要重新抛出 Python 的异常时，很多人都处理不好。本文总结了一些处理方法。

    :::python
    try:
        do_something()
    except:
        do_cleanup()

这种处理会直接把内部异常吃掉，当有问题/Bug时，会很难处理，所以不推荐。


    try:
        do_something()
    except Exception as e:
        do_cleanup()
        print e
        # or
        import traceback
        traceback.print_exc()

这种直接打印的，一是不能很好的输出到日志里。二是不能把错误交到上层调用者，不能让其知道这是有问题。

    try:
        do_somethink()
    except:
        do_cleanup()
        raise

用这种，主要是为了做cleanup。直接`raise`后，异常会抛向上层。没有catch的效果一样。

这里还有一种和上面这个类似的效果的

    try:
        do_something()
    except:
        import sys
        exc_info = sys.exc_info()
        raise exc_info[0], exc_info[1], exc_info[2]

最后，当要抛出自己重新包装后的异常时，最好把原始的异常也带上。这样有利于问题的debug。

    try:
        do_something()
    except:
        import sys
        exc_info = sys.exc_info()
        raise MyException(), None, exc_info[2]

# REF
* [Re-raising Exceptions](http://www.ianbicking.org/blog/2007/09/re-raising-exceptions.html) - by Ian Bicking
