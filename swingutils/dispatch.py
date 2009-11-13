"""
This module provides decorators and functions to easily make calls to functions
on the AWT Event Dispatch Thread, where all GUI related code should always be
run. These are necessary when you need to manipulate Swing objects from other
(non-EDT) threads in a safe manner.

"""
from threading import Event
import traceback

from java.lang import Throwable
from java.util.concurrent import RunnableFuture, ExecutionException,\
    CancellationException
from javax.swing import SwingUtilities

__all__ = ('execInEDT', 'invokeEDT', 'invokeLater', 'invokeAndWait')


class ResultHolder(RunnableFuture):
    """
    Class that stores both the function reference, and the return value or
    raised exception from an asynchronously invoked callable. Users should not
    instantiate or run these directly.

    """
    def __init__(self, func, args, kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._event = Event()

    def run(self):
        if not self._func:
            return

        try:
            self._retval = self._func(*self._args, **self._kwargs)
        except BaseException, e:
            self._exception = e
            traceback.print_exc()
        
        self._func = None        # Free any memory taken by possible closures
        self._event.set()

    def cancel(self, mayInterruptIfRunning):
        if self.isDone():
            return False
        self._func = None
        return True

    def get(self, timeout=None, unit=None):
        if timeout and unit:
            timeout = unit.toMillis(timeout) / 1000.0
        self._event.wait(timeout)
        if hasattr(self, '_exception'):
            if isinstance(self._exception, Throwable):
                raise ExecutionException(self._exception)
            raise ExecutionException(unicode(self._exception), None)
        if not hasattr(self, '_retval'):
            raise CancellationException
        return self._retval

    def isCancelled(self):
        return self._func is None

    def isDone(self):
        return hasattr(self, '_retval') or hasattr(self, '_exception')


def execInEDT(func, *args, **kwargs):
    """
    Run the given function in the Event Dispatch Thread.
    The calling thread will block until the function has been run.
    Any exceptions will be propagated to the calling thread.

    """
    if SwingUtilities.isEventDispatchThread():
        return func(*args, **kwargs)
    else:
        holder = ResultHolder(func, args, kwargs)
        SwingUtilities.invokeAndWait(holder)
        return holder.get()


def invokeEDT(func):
    """
    Decorator that ensures that the given function is executed in the Event
    Dispatch Thread. If the current thread is the EDT, the function is executed
    normally. Otherwise, it is queued for execution in the EDT. The return
    value and any raised exception are always discarded.

    """
    def wrapper(*args, **kwargs):
        if SwingUtilities.isEventDispatchThread():
            func(*args, **kwargs)
        else:
            holder = ResultHolder(func, args, kwargs)
            SwingUtilities.invokeLater(holder)
    return wrapper


def invokeLater(func):
    """
    Decorator that causes the wrapped function to be queued for execution
    in the Event Dispatch Thread. The call will return immediately.

    :return: a result holder that will contain the return value
    :rtype: :class:`~ResultHolder`

    """
    def wrapper(*args, **kwargs):
        holder = ResultHolder(func, args, kwargs)
        SwingUtilities.invokeLater(holder)
        return holder
    return wrapper


def invokeAndWait(func):
    """
    Decorator that causes the wrapped function to be queued for execution
    in the event dispatch thread. The calling thread will block
    until the function has executed in the event dispatch thread.
    If the target function is called from the event dispatch thread,
    it will be executed directly The return value of the target function
    is preserved and returned always.

    """
    def wrapper(*args, **kwargs):
        return execInEDT(func, *args, **kwargs)
    return wrapper
