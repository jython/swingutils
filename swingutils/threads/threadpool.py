from functools import wraps

from java.util.concurrent import ThreadPoolExecutor, LinkedBlockingQueue,\
    TimeUnit

from swingutils.threads.defer import AsyncToken
from swingutils.threads.util import RunnableWrapper


class _AsyncRunnable(RunnableWrapper):
    def __init__(self, func, args, kwargs):
        RunnableWrapper.__init__(self, func, args, kwargs)
        self.token = AsyncToken()

    def run(self):
        try:
            result = self._func(*self._args, **self._kwargs)
            self.token.callback(result)
        except:
            self.token.errback()


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
        runnable = _AsyncRunnable(func, args, kwargs)
        self.execute(runnable)
        return runnable.token

    def backgroundTask(self, func):
        """
        This is a decorator wrapper for :meth:`~TaskExecutor.runBackground`.

        :rtype: :class:`~AsyncToken`

        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.runBackground(func, *args, **kwargs)
        return wrapper
