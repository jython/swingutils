from functools import wraps

from java.lang import Runnable
from java.util.concurrent import ThreadPoolExecutor, TimeUnit, \
    LinkedBlockingQueue, Callable, FutureTask
from javax.swing import SwingUtilities

__all__ = ('RunnableWrapper', 'CallableWrapper', 'TaskExecutor', 'runSwing',
           'swingTask', 'runAsyncSwing', 'asyncSwingTask')


class RunnableWrapper(Runnable):
    """
    Wraps a callable and its arguments for use in Java code that requires a
    :class:`~java.lang.Runnable`.

    """
    def __init__(self, func, args, kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def run(self):
        self._func(*self._args, **self._kwargs)


class CallableWrapper(Callable):
    """
    Wraps a callable and its arguments for use in Java code that requires a
    :class:`~java.util.concurrent.Callable`.

    """
    def __init__(self, func, args, kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def call(self):
        return self._func(*self._args, **self._kwargs)


class TaskExecutor(ThreadPoolExecutor):
    """
    This is a configurable thread pool for executing background tasks.
    
    :param coreThreads: Minimum number of threads
    :param maxThreads: Maximum number of threads
    :param keepalive: Time in seconds to keep idle non-core threads alive
    :param queue: The queue implementation, defaults to a
                  :class:`~java.util.concurrent.LinkedBlockingQueue`

    .. seealso:: :class:`java.util.concurrent.ThreadPoolExecutor`

    """
    def __init__(self, coreThreads=1, maxThreads=1, keepalive=5, queue=None):
        queue = queue or LinkedBlockingQueue()
        ThreadPoolExecutor.__init__(self, coreThreads, maxThreads, keepalive,
                                    TimeUnit.SECONDS, queue)

    def runBackground(self, func, *args, **kwargs):
        """
        Queues a (Python) callable for background execution in this thread
        pool. Any extra positional and keyword arguments will be passed to the
        target callable.

        """
        runnable = RunnableWrapper(func, args, kwargs)
        self.execute(runnable)

    def backgroundTask(self, func):
        """
        This is a decorator wrapper for :meth:`~TaskExecutor.runBackground`.

        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.runBackground(func, *args, **kwargs)
        return wrapper

#
# Functions for running code in the Event Dispatch Thread
#

def runSwing(func, *args, **kwargs):
    """
    Runs the given function in the Event Dispatch Thread.
    The calling thread will block until the function has been run.
    Any extra positional and keyword arguments will be passed to the
    target function.

    """
    if SwingUtilities.isEventDispatchThread():
        return func(*args, **kwargs)
    else:
        callable = CallableWrapper(func, args, kwargs)
        task = FutureTask(callable)
        SwingUtilities.invokeAndWait(task)
        return task.get()


def swingTask(func):
    """
    This is a decorator wrapper for :func:`runSwing`.

    This causes the wrapped function to be executed
    in the event dispatch thread. The calling thread will block
    until the function has finished executing.
    If the target function is called from the event dispatch thread,
    it will be executed directly.

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return runSwing(func, *args, **kwargs)
    return wrapper


def runAsyncSwing(func, *args, **kwargs):
    """
    Queues the given callable to be executed in the Event Dispatch Thread.
    Any extra positional and keyword arguments will be passed to the
    target function. This function returns immediately with no return value.

    :rtype: :class:`~java.util.concurrent.Future`

    """
    callable = CallableWrapper(func, args, kwargs)
    task = FutureTask(callable)
    SwingUtilities.invokeLater(task)


def asyncSwingTask(func):
    """
    This is a decorator wrapper for :func:`runAsyncSwing`.

    This causes the wrapped function to be queued for execution
    in the Event Dispatch Thread. The call will return immediately with no
    return value.

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        runAsyncSwing(func, *args, **kwargs)
    return wrapper
