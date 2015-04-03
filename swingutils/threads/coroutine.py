"""
A coroutine mechanism that uses the AWT event loop.

"""
from functools import wraps
from types import GeneratorType
from functools import partial
from concurrent.futures import Future
import sys

from swingutils.threads.swing import swingRun

__all__ = ('returnValue', 'swingCoroutine')


class _ReturnValue(BaseException):
    def __init__(self, result):
        self.result = result


def returnValue(result):
    """
    Returns a value from an @swingCoroutine function. Since they are
    generators, a normal ``return`` statement can't be used on Jython 2.x.

    """
    raise _ReturnValue(result)


def isFuture(obj):
    return hasattr(obj, 'add_done_callback') and hasattr(obj, 'result') and \
        hasattr(obj, 'exception')


@swingRun
def _swingCoroutine(future, g, parentFuture):
    while True:
        try:
            # Take advantage of the exception_info() method on the futures
            # backport which contains the traceback since exceptions don't
            # have __traceback__ on Python 2.x
            exc = future.exception()
            if exc:
                tb = None
                if hasattr(future, 'exception_info'):
                    exc, tb = future.exception_info()
                else:
                    exc = future.exception()
                result = g.throw(type(exc), exc, tb)
            else:
                result = g.send(future.result())
        except StopIteration as e:
            # StopIteration.value is set on Python 3 when the return
            # statement is used with a value
            value = getattr(e, 'value', None)
            parentFuture.set_result(value)
            return
        except _ReturnValue as e:
            parentFuture.set_result(e.result)
            return
        except BaseException as e:
            # Take advantage of the backport again if possible
            if hasattr(parentFuture, 'set_exception_info'):
                parentFuture.set_exception_info(*sys.exc_info()[1:])
            else:
                parentFuture.set_exception(e)
            return

        if isFuture(result):
            callback = partial(_swingCoroutine, g=g,
                               parentFuture=parentFuture)
            result.add_done_callback(callback)
            return


def swingCoroutine(func):
    """
    Enables the wrapped function to pause execution every time it needs a
    Future to be completed to continue. If the wrapped function is a
    generator, it will run it on the AWT event loop until either
    returnValue() is called or the execution reaches the end of the function.

    :rtype: :class:`~Future`

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        g = func(*args, **kwargs)

        # Pass through the result if it was a Future
        if isFuture(g):
            return g

        # If func was a regular function and not a generator, simply return
        # its return value. Otherwise start executing the code and return a
        # Future.
        future = Future()
        if isinstance(g, GeneratorType):
            subFuture = Future()
            subFuture.set_result(None)
            _swingCoroutine(subFuture, g, future)
        else:
            future.set_result(g)

        return future

    return wrapper
