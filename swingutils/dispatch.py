"""
This module provides decorators and functions to easily make calls to functions
on the AWT Event Dispatch Thread, where all GUI related code should always be
run. These are necessary when you need to manipulate Swing objects from other
(non-EDT) threads in a safe manner.

"""

from threading import Event

from java.util.concurrent import RunnableFuture, ExecutionException,\
    CancellationException
from javax.swing import SwingUtilities

__all__ = ('execInEDT', 'invokeLater', 'invokeAndWait')


class ResultHolder(RunnableFuture):
    """Class that stores both the function reference, and the return value or
    raised exception from an asynchronously invoked callable. Users should not
    instantiate or run these directly.

    """
    __slots__ = ('_retval', '_exception')

    def __init__(self, func, args, kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._event = Event()

    def run(self):
        func = getattr(self, '_func', None)
        if not func:
            return

        try:
            self._retval = func(*self._args, **self._kwargs)
        except BaseException, e:
            self._exception = e
        
        self.func = None        # Free any memory taken by possible closures
        self._event.set()

    def cancel(self, mayInterruptIfRunning):
        if self.isDone():
            return False
        del self.func
        return True

    def get(self, timeout=None, unit=None):
        if timeout and unit:
            timeout = unit.toMillis(timeout) / 1000.0
        self._event.wait(timeout)
        if hasattr(self, '_exception'):
            raise ExecutionException(self._exception)
        if not hasattr(self, '_retval'):
            raise CancellationException
        return self.retval

    def isCancelled(self):
        return not hasattr(self, '_func')

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
