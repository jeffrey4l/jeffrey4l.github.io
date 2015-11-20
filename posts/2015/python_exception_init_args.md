title: Python Exception init args
Date: 2015-11-20
Category: Programming
Tags: Python
Slug: python-exception-init-args

<div style="text-align: center;">
<img src="images/talk_is_cheap.jpg"/>
</div>

一直没有搞明白 `Exception` 的 args 和 message 参数, 最近看了一下 CPython 源码，
终于搞明白了。

一开始(从2.5开始)的时候是有 `args` 和 `message` 两个参数的。2.6版本之后，把
`message` 废弃掉了，只留下了一个任意长度的 `args`。

以下是2.5以后的代码，可以看到，如果args 长度是1，就会把 `self.message = args[0]`

```c
static PyObject *
BaseException_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyBaseExceptionObject *self;

    self = (PyBaseExceptionObject *)type->tp_alloc(type, 0);
    if (!self)
        return NULL;
    /* the dict is created on the fly in PyObject_GenericSetAttr */
    self->message = self->dict = NULL;

    self->args = PyTuple_New(0);
    if (!self->args) {
        Py_DECREF(self);
        return NULL;
    }

    self->message = PyString_FromString("");
    if (!self->message) {
        Py_DECREF(self);
        return NULL;
    }

    return (PyObject *)self;
}

static int
BaseException_init(PyBaseExceptionObject *self, PyObject *args, PyObject *kwds)
{
    if (!_PyArg_NoKeywords(Py_TYPE(self)->tp_name, kwds))
        return -1;

    Py_DECREF(self->args);
    self->args = args;
    Py_INCREF(self->args);

    if (PyTuple_GET_SIZE(self->args) == 1) {
        Py_CLEAR(self->message);
        self->message = PyTuple_GET_ITEM(self->args, 0);
        Py_INCREF(self->message);
    }
    return 0;
}

```

本来 message 就是 Exception的一个属性，在2.6以后，把它变成了一个 descriptor, 当
调用时，如果它在 `self.__dict__` 里，就直接打印，否则就返回 `self.message` 的信息
并打印出一个 `Warning`。如果已经赋过一个值的话` self.message = xxxx`, 它就会存在
`self.__dict__`里。

```c
static PyObject *
BaseException_get_message(PyBaseExceptionObject *self)
{
    PyObject *msg;

    /* if "message" is in self->dict, accessing a user-set message attribute */
    if (self->dict &&
        (msg = PyDict_GetItemString(self->dict, "message"))) {
        Py_INCREF(msg);
        return msg;
    }

    if (self->message == NULL) {
        PyErr_SetString(PyExc_AttributeError, "message attribute was deleted");
        return NULL;
    }

    /* accessing the deprecated "builtin" message attribute of Exception */
    if (PyErr_WarnEx(PyExc_DeprecationWarning,
                     "BaseException.message has been deprecated as "
                     "of Python 2.6", 1) < 0)
        return NULL;

    Py_INCREF(self->message);
    return self->message;
}


static int
BaseException_set_message(PyBaseExceptionObject *self, PyObject *val)
{
    /* if val is NULL, delete the message attribute */
    if (val == NULL) {
        if (self->dict && PyDict_GetItemString(self->dict, "message")) {
            if (PyDict_DelItemString(self->dict, "message") < 0)
                return -1;
        }
        Py_XDECREF(self->message);
        self->message = NULL;
        return 0;
    }

    /* else set it in __dict__, but may need to create the dict first */
    if (self->dict == NULL) {
        self->dict = PyDict_New();
        if (!self->dict)
            return -1;
    }
    return PyDict_SetItemString(self->dict, "message", val);
}

```

在 python3 中，message 相关的信息已经完全删除掉了。

所以，一般使用 `message` 属性的话，推荐这样使用

```
class MyException(Exception):
    def __init__(self, message):
        self.message = message

class My2Exception(Exception):
    message = 'this is a message'
```
