"""
This module provides decorators and functions to easily make calls to functions
on the AWT Event Dispatch Thread, where all GUI related code should always be
run. These are necessary when you need to manipulate Swing objects from other
(non-EDT) threads in a safe manner.

"""
from javax.swing import SwingUtilities

from swingutils.threads import RunnableWrapper, AsyncResult

__all__ = ('execInEDT', 'invokeInEDT', 'invokeLater', 'invokeAsync')


def execInEDT(func, *args, **kwargs):
    """
    Run the given function in the Event Dispatch Thread.
    The calling thread will block until the function has been run.
    Any exceptions will be propagated to the calling thread.

    """
    if SwingUtilities.isEventDispatchThread():
        return func(*args, **kwargs)
    else:
        holder = AsyncResult(func, args, kwargs)
        SwingUtilities.invokeAndWait(holder)
        return holder.get()


def invokeInEDT(func):
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


def invokeLater(func):
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
            wrapper = RunnableWrapper(func, args, kwargs)
            SwingUtilities.invokeLater(wrapper)
    return wrapper


def invokeAsync(func):
    """
    Decorator that causes the wrapped function to be queued for execution
    in the Event Dispatch Thread. The call will return immediately.

    :return: a result holder that will contain the return value
    :rtype: :class:`~AsyncResult`

    """
    def wrapper(*args, **kwargs):
        holder = AsyncResult(func, args, kwargs)
        SwingUtilities.invokeLater(holder)
        return holder
    return wrapper
