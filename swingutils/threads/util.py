from __future__ import unicode_literals
from types import MethodType
import inspect

from java.lang import Runnable, Thread
from java.util.concurrent import Callable

__all__ = ('RunnableWrapper', 'CallableWrapper', 'setDefaultExceptionHandler')


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


class PythonUncaughtExceptionHandler(Thread.UncaughtExceptionHandler):
    def __init__(self, handler):
        self.handler = handler

    def uncaughtException(self, thread, exception):
        self.handler(thread, exception)


def setDefaultExceptionHandler(func):
    """
    Sets the default handler for uncaught exceptions for all threads.
    A value of ``None`` removes the default handler.

    The handler is called with two arguments: the java.lang.Thread object and
    the exception instance.

    """

    if func is None:
        handler = None
    else:
        argspec = inspect.getargspec(func)
        min_args = 3 if isinstance(func, MethodType) else 2
        if len(argspec.args) < min_args and not argspec.varargs:
            raise TypeError('The handler must accept at least two positional arguments')

        handler = PythonUncaughtExceptionHandler(func)

    Thread.setDefaultUncaughtExceptionHandler(handler)
