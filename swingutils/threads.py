from java.lang import Runnable
from java.util.concurrent import (ThreadPoolExecutor, TimeUnit,
                                  LinkedBlockingDeque)

__all__ = ('TaskExecutor',)

class RunnableWrapper(Runnable):
    def __init__(self, func, args, kwargs, name=None, beforeCallback=None,
                 afterCallback=None):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.name = name
        self.beforeCallback = beforeCallback
        self.afterCallback = afterCallback

    def run(self):
        self.func(*self.args, **self.kwargs)


class TaskExecutor(ThreadPoolExecutor):
    beforeCallback = None
    afterCallback = None

    def __init__(self, coreThreads=1, maxThreads=1, keepalive=5, queue=None,
                 beforeCallback=None, afterCallback=None):
        queue = queue or LinkedBlockingDeque()
        ThreadPoolExecutor.__init__(self, coreThreads, maxThreads, keepalive,
                                    TimeUnit.SECONDS, queue)
        self.beforeCallback = beforeCallback
        self.afterCallback = afterCallback

    def beforeExecute(self, thread, runnable):
        if self.beforeCallback:
            self.beforeCallback(thread, runnable)
        if runnable.beforeCallback:
            runnable.beforeCallback(thread, runnable)

    def afterExecute(self, runnable, throwable):
        if self.afterCallback:
            self.afterCallback(runnable, throwable)
        if runnable.afterCallback:
            runnable.afterCallback(runnable, throwable)

    def task(self, func):
        def wrapper(*args, **kwargs):
            runnable = RunnableWrapper(func, args, kwargs)
            self.execute(runnable)
        return wrapper

    def namedTask(self, name, beforeCallback=None, afterCallback=None):
        def outer(func):
            def inner(*args, **kwargs):
                runnable = RunnableWrapper(func, args, kwargs, name,
                                           beforeCallback, afterCallback)
                self.execute(runnable)
            return inner
        return outer

    def runTask(self, func, *args, **kwargs):
        runnable = RunnableWrapper(func, args, kwargs)
        self.execute(runnable)

    def runNamedTask(self, func, name, *args, **kwargs):
        runnable = RunnableWrapper(func, args, kwargs, name)
        self.execute(runnable)
