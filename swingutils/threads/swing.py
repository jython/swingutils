"""
Functions for running code in the Event Dispatch Thread.

"""
from __future__ import unicode_literals
from functools import wraps

from java.util.concurrent import FutureTask
from javax.swing import SwingUtilities

from swingutils.threads.util import CallableWrapper, RunnableWrapper


def callSwing(func, *args, **kwargs):
    """
    Runs the given function in the Event Dispatch Thread.
    If this is invoked inside the EDT, the given function will be run normally.
    Otherwise, it'll be queued to be run and the calling thread will block
    until the function has been executed.

    :return: func's return value

    """
    if SwingUtilities.isEventDispatchThread():
        return func(*args, **kwargs)

    callable = CallableWrapper(func, args, kwargs)
    task = FutureTask(callable)
    SwingUtilities.invokeAndWait(task)
    return task.get()


def swingCall(func):
    """
    This is a decorator wrapper for :func:`callSwing`.

    This causes the wrapped function to be executed
    in the event dispatch thread. The calling thread will block
    until the function has finished executing.
    If the target function is called from the event dispatch thread,
    it will be executed directly.

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return callSwing(func, *args, **kwargs)
    return wrapper


def runSwing(func, *args, **kwargs):
    """
    Runs the given function in the Event Dispatch Thread.
    If this is invoked inside the EDT, the given function will be run normally.
    Otherwise, it'll be queued to be run later.
    The return value from the target function will not be available.

    :return: None

    """
    if SwingUtilities.isEventDispatchThread():
        func(*args, **kwargs)
    else:
        runnable = RunnableWrapper(func, args, kwargs)
        SwingUtilities.invokeLater(runnable)


def swingRun(func):
    """
    This is a decorator wrapper for :func:`runSwing`.

    This causes the wrapped function to be executed in the
    Event Dispatch Thread. If the target function is called from the EDT,
    it will be executed directly. Otherwise, it'll be queued to be run later.
    The return value from the wrapped function will not be available.

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        runSwing(func, *args, **kwargs)
    return wrapper


def runSwingLater(func, *args, **kwargs):
    """
    Queues the given task to be run in the Event Dispatch Thread, regardless
    of whether the calling thread is the EDT itself.

    """
    runnable = RunnableWrapper(func, args, kwargs)
    SwingUtilities.invokeLater(runnable)


def swingRunLater(func):
    """
    This is a decorator wrapper for :func:`runSwingLater`.

    This causes the wrapped function to be queued for execution in the
    Event Dispatch Thread. The call returns immediately, regardless of which
    thread it was made from.

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        runSwingLater(func, *args, **kwargs)
    return wrapper
