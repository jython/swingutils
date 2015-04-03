from __future__ import unicode_literals

from java.lang import Runnable
from java.util.concurrent import Callable

__all__ = ('RunnableWrapper', 'CallableWrapper')


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
