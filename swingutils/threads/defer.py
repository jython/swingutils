"""
A simplified version of Twisted's deferred execution mechanism.

"""
from functools import wraps
from collections import deque
from types import GeneratorType
import sys

from swingutils.threads.swing import swingRun

__all__ = ('Failure', 'AsyncToken', 'returnValue', 'inlineCallbacks')


class Failure(object):
    def __init__(self, type, value, traceback):
        self.type = type
        self.value = value
        self.traceback = traceback

    def throw(self, g):
        return g.throw(self.type, self.value, self.traceback)
    
    def raiseException(self):
        raise self.type, self.value, self.traceback

    def __repr__(self):
        valuestr = self.value
        if isinstance(valuestr, unicode):
            valuestr = valuestr.decode('ascii', 'replace') 
        return '<%s, exception=%s>' % (self.__class__.__name__, valuestr)


class AlreadyCalledError(Exception):
    pass


def _passthru(arg):
    return arg


class AsyncToken(object):
    """
    Handle for an asynchronously executed task. This is similar to
    (but incompatible with) Twisted's deferred class. These are produced by
    the :class:`~swingutils.threads.threadpool.TaskExecutor` class and
    functions decorated with @inlineCallbacks. Users should not normally
    instantiate these manually.

    """
    _called = False
    _result = None

    def __init__(self):
        self._callbacks = deque()

    def callback(self, result):
        self._result = result
        self._runCallbacks()

    def errback(self):
        self._result = Failure(*sys.exc_info())
        self._runCallbacks()

    def _runCallbacks(self):
        if self._called:
            raise AlreadyCalledError

        self._called = True
        while self._callbacks:
            callback, args, kwargs = self._callbacks.popleft()
            try:
                self._result = callback(self._result, *args, **kwargs)
            except:
                self._result = Failure(*sys.exc_info())

        # Raise any unhandled exceptions
        if isinstance(self._result, Failure):
            self._result.raiseException()

    def addCallback(self, func, *args, **kwargs):
        if not hasattr(func, '__call__'):
            raise ValueError('func is not callable')

        if self._called:
            func(self._result, *args, **kwargs)
        else:
            self._callbacks.append((func, args, kwargs))


class _ReturnValue(BaseException):
    def __init__(self, result):
        self.result = result


def returnValue(result):
    """
    Returns a value from an @inlineCallbacks function. Since they are
    generators, a normal ``return`` statement can't be used.

    """
    raise _ReturnValue(result)


@swingRun
def _inlineCallbacks(result, g, token):
    while True:
        try:
            if isinstance(result, Failure):
                result = result.throw(g)
            else:
                result = g.send(result)
        except StopIteration:
            token.callback(None)
            return
        except _ReturnValue, e:
            token.callback(e.result)
            return
        except:
            token.errback()
            return

        if isinstance(result, AsyncToken):
            result.addCallback(_inlineCallbacks, g, token)
            return


def inlineCallbacks(func):
    """
    Enables the wrapped function to execute code running in other threads in
    a synchronous manner by creative use of the generators system.

    :rtype: :class:`~AsyncToken`

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        g = func(*args, **kwargs)
        token = AsyncToken()

        # If func was a regular function and not a generator, simply return
        # its return value. Otherwise start executing the code and return an
        # AsyncToken.
        if not isinstance(g, GeneratorType):
            token._result = g
            token._called = True
        else:
            _inlineCallbacks(None, g, token)
        return token
    return wrapper
