Threads
=======

This module aims to help with two mutually related tasks:

* Running background tasks in separate threads
* Safely calling GUI code from background threads

All properly designed GUI applications execute potentially long running
operations in separate threads to prevent the interface from becoming
unresponsive. This, on the other hand, creates new challenges because often,
the code in the background thread needs to access the GUI. Java 6 incorporated
the :class:`~javax.swing.SwingWorker` class to help with this, but even this
solution is quite clumsy when compared to what the flexible Python
language can accomplish. Jython-Swingutils has a mechanism, inspired by the
`Twisted <http://twistedmatrix.com/>`_ framework, that makes switching between
threads almost seamless.

Thread pools
------------

To run background tasks, you first need to create a thread pool.
The :class:`~swingutils.threads.threadpool.TaskExecutor` class is basically
Java's ThreadPoolExecutor with some sugar topping that lets it cooperate with
Python better.

Background tasks can be submitted either directly, via
:meth:`~swingutils.threads.threadpool.TaskExecutor.runBackground` or by
decorating a function with
:meth:`~swingutils.threads.threadpool.TaskExecutor.backgroundTask`.

Example::

    from swingutils.threads.threadpool import TaskExecutor
    
    def hello(name):
       print 'Hello, %s' % name
    
    executor = TaskExecutor()
    executor.runBackground(hello, 'world')

This will print "Hello, world" from a background thread. The functionally
equivalent version using the decorator form is this::

    from swingutils.threads.threadpool import TaskExecutor

    executor = TaskExecutor()

    @executor.backgroundTask
    def hello(name):
       print 'Hello, %s' % name

    hello('world')

Running GUI code from background threads
----------------------------------------

When you need to manipulate live GUI components from background threads,
you need to make sure that any code doing so executes in the
`Event Dispatch Thread <http://download.oracle.com/javase/tutorial/uiswing/concurrency/dispatch.html>`_
(EDT) to avoid thread safety issues. There are several different ways you can do
this, depending on whether you want the calling thread to block or not, and how
to deal with calls already originating from the EDT.

The easiest way to deal with GUI calls is to use
:func:`~swingutils.threads.swing.callSwing` or its decorator form,
:func:`~swingutils.threads.swing.swingCall`::

    from swingutils.threads.swing import callSwing

    def fillInExchangeRate():
        rate = fetchExchangeRate('USD', 'EUR')
        callSwing(rateField.setValue, rate)

The following table lists the differences between the various different
GUI call mechanisms:

===========================  =====================  ================================
Function                     Blocks calling thread  Blocks EDT if called from within
===========================  =====================  ================================
callSwing/swingCall          Yes                    Yes
runSwing/swingRun            No                     Yes
runSwingLater/swingRunLater  No                     No
===========================  =====================  ================================

Using @swingCoroutine
---------------------

So we have the means to execute code in background threads and to execute
GUI code from those threads. This is however not the best we can do with
Python. If you have a complex event chain that requires bouncing between
background and GUI threads, things can get quite messy.

Enter the **@swingCoroutine** decorator. Decorating a function with this
allows the execution to "adjourn" while waiting for the background task to
complete, freeing the EDT to attend to other tasks while waiting. Observe::

    from swingutils.threads.defer import swingCoroutine
    from swingutils.threads.threadpool import TaskExecutor

    executor = TaskExecutor()

    @swingCoroutine
    def fillInExchangeRates(rates):
        for rateField, curr1, curr2 in rates:
            rate = yield executor.runBackground(fetchExchangeRate, curr1, curr2)
            rateField.setValue(rate)

The code wrapped by @swingCoroutine always run in the EDT. What happens here
is that it runs until a request is made to fetch an exchange rate in a
background thread. At that point, the execution is "adjourned" and the EDT
returns to processing its own queue. When fetchExchangeRate() returns, it
causes a new task to be pushed to the EDT processing queue that resumes
execution of the fillInExchangeRates() function.

Technically this was implemented using Python's generator mechanism, which
unfortunately adds a few restrictions:

* You must use the ``yield`` statement when executing other functions that
  return an :class:`~concurrent.futures.Future` (such as those decorated by
  @swingCoroutine)
* The "return" statement can't be used on Jython 2.x -- use
  :func:`~swingutils.threads.defer.returnValue` instead
* Don't catch BaseException in a block that calls returnValue() since it is
  implemented as an exception behind the scenes

The ``yield`` statement can be safely used when calling functions from an
@swingCoroutine decorated function. Doing so ensures proper handling of
any returned Futures.
