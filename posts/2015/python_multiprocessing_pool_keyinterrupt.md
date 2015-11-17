title: Interrupt the Python multiprocessing.Pool in graceful way
Date: 2015-11-17
Tags: Python
Category: Programming
Slug: interrupt-the-python-multiprocessing-pool-in-graceful-way

When using `KeyboardInterrupt`(`Ctrl+c`) interrupt the excution of the `multiprocess.Pool`, it will not work as expected. Following is a demo

```python
import time
from multiprocessing import Pool


def worker():
    while True:
        time.sleep(1)

pool = Pool(1)

pool.apply(worker)

```

When run the code and try to `Ctrl+C` to stop it, it will never be stopped.

```
$ python2 b.py                                                                      
^CProcess PoolWorker-1:
Traceback (most recent call last):
  File "/usr/lib/python2.7/multiprocessing/process.py", line 258, in _bootstrap
    self.run()
  File "/usr/lib/python2.7/multiprocessing/process.py", line 114, in run
    self._target(*self._args, **self._kwargs)
  File "/usr/lib/python2.7/multiprocessing/pool.py", line 113, in worker
    result = (True, func(*args, **kwds))
  File "b.py", line 7, in worker
    time.sleep(1)
KeyboardInterrupt
```

The root cause is explained in [stackoverflow](http://stackoverflow.com/a/1408476/893981). And the bug is [here](http://bugs.python.org/issue8296)

<blockquote>
This is a Python bug. When waiting for a condition in threading.Condition.wait(), KeyboardInterrupt is never sent. Repro:

<pre>
import threading
cond = threading.Condition(threading.Lock())
cond.acquire()
cond.wait(None)
print "done"
</pre>

The KeyboardInterrupt exception won't be delivered until wait() returns, and it never returns, so the interrupt never happens. KeyboardInterrupt should almost certainly interrupt a condition wait.

Note that this doesn't happen if a timeout is specified; cond.wait(1) will receive the interrupt immediately. So, a workaround is to specify a timeout. To do that, replace

<pre>
    results = pool.map(slowly_square, range(40))
</pre>

with

<pre>
    results = pool.map_async(slowly_square, range(40)).get(9999999)
</pre>

or similar.
</blockquote>

By using this, we can interrupt the Pool by using `Ctrl+c`.

Here is a better version.

```python
import multiprocessing
from multiprocessing import Pool
import time
import signal


def worker():
    while True:
        print time.time()
        time.sleep(.5)

def worker_init():
    # ignore the SIGINI in sub process, just print a log
    def sig_int(signal_num, frame):
        print 'signal: %s' % signal_num
    signal.signal(signal.SIGINT, sig_int)


pool = Pool(2, worker_init)
result = pool.apply_async(worker)
while True:
    try:
        result.get(0xfff)
    # catch TimeoutError and get again
    except multiprocessing.TimeoutError as ex:
        print 'timeout'
```

# REF

* [Python Bug](http://bugs.python.org/issue8296)
* [How Ctrl+c works](http://unix.stackexchange.com/a/149756)
* [Keyboard Interrupts with python's multiprocessing Pool](http://stackoverflow.com/a/1408476/893981)
