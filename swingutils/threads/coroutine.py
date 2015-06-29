"""
A coroutine mechanism that uses the AWT event loop.

"""
from functools import wraps
from functools import partial
from concurrent.futures import Future
from inspect import isgeneratorfunction
import sys

from swingutils.threads.swing import runSwing

__all__ = ('returnValue', 'swingCoroutine')

_defaultExceptionHandler = None


def returnValue(result):
    """
    Returns a value from an @swingCoroutine function. Since they are
    generators, a normal ``return`` statement can't be used on Jython 2.x.

    """
    exception = StopIteration()
    exception.value = result
    raise exception


def isFuture(obj):
    return (hasattr(obj, 'add_done_callback') and hasattr(obj, 'result') and
            hasattr(obj, 'exception'))


def _swingCoroutine(future, g, parentFuture):
    try:
        exc = future.exception()
        if exc:
            # Take advantage of the exception_info() method on the futures
            # backport which contains the traceback since exceptions don't
            # have __traceback__ on Python 2.x
            if hasattr(future, 'exception_info'):
                exc, tb = future.exception_info()
            else:
                exc, tb = future.exception(), None

            result = g.throw(type(exc), exc, tb)
        else:
            result = g.send(future.result())

        if not isFuture(result):
            raise TypeError(
                'A @swingCoroutine must only yield Futures -- '
                'received {} instead'.format(result.__class__.__name__))

        callback = partial(runSwing, _swingCoroutine, g=g,
                           parentFuture=parentFuture)
        result.add_done_callback(callback)
    except StopIteration as e:
        # StopIteration.value is set on Python 3 when the return
        # statement is used with a value
        value = getattr(e, 'value', None)
        parentFuture.set_result(value)
    except BaseException as e:
        # Take advantage of the backport if possible
        excInfo = sys.exc_info()
        if hasattr(parentFuture, 'set_exception_info'):
            parentFuture.set_exception_info(*excInfo[1:])
        else:
            parentFuture.set_exception(e)

        if _defaultExceptionHandler and not parentFuture._done_callbacks:
            _defaultExceptionHandler(*excInfo)


def swingCoroutine(func):
    """
    Enables the wrapped generator function to pause execution when it needs a
    Future to be completed to continue. The wrapped function is guaranteed to
    run on the AWT event dispatch thread. To return a value from it on
    Jython 2, call :func:`returnValue` instead of using the `return`
    statement.

    If there is unhandled exception in the wrapped method and the future
    returned from the wrapper has no listener callbacks, the default coroutine
    exception handler is invoked.

    """

    if not isgeneratorfunction(func):
        raise TypeError('The wrapped function must be a generator function')

    @wraps(func)
    def wrapper(*args, **kwargs):
        g = func(*args, **kwargs)
        future = Future()
        subFuture = Future()
        subFuture.set_result(None)
        runSwing(_swingCoroutine, subFuture, g, future)
        return future

    return wrapper


def setDefaultCoroutineExceptionHandler(handler):
    """
    Sets the default handler for unhandled exceptions in @swingCoroutines.

    The handler receives three arguments: exception type, exception instance,
    traceback object.
    """

    global _defaultExceptionHandler
    _defaultExceptionHandler = handler
