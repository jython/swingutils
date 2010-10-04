Binding
=======

Binding is a mechanism for keeping properties between two objects synchronized.
This can be very useful for providing data to UI components like form fields,
lists, tables etc., but it is by no means limited to that.


Simple example
--------------

::

	from swingutils.binding import BindingGroup
	
	group = binding.BindingGroup()
	group.bind(object1, 'property', object2, 'anotherproperty')

This is the simplest form of using binding. It creates a new binding group and
makes a one-way binding from ``object1.property`` to ``object2.anotherproperty``.
This means that whenever object1.property is assigned another property, it is
automatically copied to object2.anotherproperty. The only requirement for this
to work is that object1 has support for
`bound properties <http://download.oracle.com/javase/tutorial/javabeans/properties/bound.html>`_.
See the :ref:`Beans section <beans>` for more information on how to accomplish
that.

You can also have object2.anotherproperty to be synced back to object1.property
by means of two way binding::

	from swingutils.binding import BindingGroup, TWOWAY

	group = binding.BindingGroup()
	group.bind(object1, 'property', object2, 'anotherproperty', mode=TWOWAY)

For bidirectional synchronization to work properly, object2 also needs to
support bound properties.


Asymmetric binding
------------------

If you need two convert the values in a two way binding, you need to make
two separate one way bindings between the objects. If, for example, you need
to convert a numeric value to text and vice versa, you can do this::

    from datetime import datetime
	from swingutils.binding import BindingGroup

    def parseDate(dateText):
        return datetime.strptime(dateText, '%Y-%m-%d')

    group = binding.BindingGroup(vars={'parseDate': parseDate})
    group.bind(dateField, 'parseDate(text)', person, 'birthDate')
    group.bind(person, 'str(birthDate)', dateField, 'text')

This converts the values from string to datetime and back as necessary.
Note how the external parseDate function was used in a binding expression by
introducing it as a variable in the binding group.


How it works
------------

To understand how to take full advantage of Swingutils Binding, you should get
acquainted with some of its basic concepts.

A **binding group** is a container for a number of bindings. The purpose of
storing bindings in groups is twofold. First, it enables you to manually
synchronize a number of bindings at once with a simple method call. Second,
it's a convenient way to set default options for bindings.

A **binding** is an object that handles the synchronization of two properties.
It contains references to the source and target objects and their respective
binding expressions.

A **binding expression** is the container for the actual expression. When it is
`bound` (by the Binding object that owns it), it parses the expression into one
or more `binding chains`. In addition, the expression object implements
read/write operations for the expression.

A **binding chain** is a linked list of nodes created from some part of the
binding expression they belong to. Consider the following binding::

    from swingutils.binding import BindingGroup

    person = Person()
    group = BindingGroup()
    group.bind(person, 'employer.name.startswith("Nok") and homecity == "Espoo"',
               matchCheckbox, 'selected')


The source expression contains two chains, which you can print with ``group.dump()``:

.. code-block:: none

    Binding 1:
      Source:
        Source code: employer.name.startswith("Nok") and homecity == "Espoo"
        Chain 1: Attribute(employer) -> Attribute(name) -> Attribute(startswith) -> Call
        Chain 2: Attribute(homecity)
      Target:
        Source code: selected
        Chain 1: Attribute(selected)

What this binding does is that it marks the checkbox selected if and only if
the person's employer's name starts with "Nok" and the person's home city is
"Espoo". The expression is automatically re-evaluated when the person switches
employers, the employer changes its name or the person moves to another city.


Binding options
---------------

These are options that can be passed as keyword arguments to the constructor
of :class:`~swingutils.binding.BindingGroup` or to its
:meth:`~swingutils.binding.BindingGroup.bind` method.

In addition to these, various adapters have their own options. See the
adapters section for specifics.

============    ===============================================================
Option          Definition
============    ===============================================================
mode            Synchronization mode (integer). Available options are:
                
                * MANUAL (0): No automatic synchronization
                * ONEWAY (1): Copy source to target when source changes
                * TWOWAY (2): Like ONEWAY but also copy target to source
                  when target changes
                
                These constants can be imported from :mod:`swingutils.binding`.

vars            A dictionary of extra variables that are available in binding
                expressions. Useful for importing functions and other
                variables. The dict is copied when binding, and you should
                not attempt to modify the values afterwards.

ignoreErrors    If ``True``, then any exceptions raised during
                synchronization ignored (but still logged). If this happens
                during source expression evaluation, then an error value
                specified by the `errorValue` option is
                written to the location specified by the target expression.
                
                Default is ``True``.

errorValue      The value that is copied to the target location when
                reading from the source expression fails during
                synchronization.

                Default is ``None``.

logger          A :class:`logging.Logger` object that will be used for
                logging debugging information to aid the developer in
                figuring out why an expression is not working as intended.

                Default is ``None``.
============    ===============================================================


Adapters
--------

Adapters are helper classes that Binding uses automatically when needed to
facilitate binding to properties that don't report of changes in their values
like normal JavaBeans properties. An example of this would be the `text`
property in the commonly used :class:`~javax.swing.JTextField` class. Instead
of firing a property change for the `text` property, this class fires a
document change event that details the change made to the document. The
adapter for JTextField allows you to use the `text` property as if it fired
property change events normally by actually listening to document change
events.

Adapter options
"""""""""""""""

The following table lists the options for all built-in adapters. These can be
given as keyword arguments when binding (or when creating a binding group).

===============  =================  ===========================================
Option           Used for           Effect
===============  =================  ===========================================
onFocusLost      JTextComponent     When ``True``, triggers an update only on
                                    a focus lost event. ``False`` triggers
                                    updates on any change to the underlying
                                    Document.
                                    
                                    Default is ``False``.

ignoreAdjusting  JList, JTable      When ``True``, triggers an update only on
                                    a finished selection change event.
                                    ``False`` triggers updates on each and
                                    every selection change event.
                                    
                                    Default is ``True``.
===============  =================  ===========================================


Debugging bindings
------------------

By default, bindings generate no error messages, so if they don't work as you
would expect, it can sometimes be hard to determine why. One options is to set
the ``ignoreErrors`` options to ``False``, so it will raise any exceptions
encountered while synchronizing properties. This can easily get disruptive,
though. A better alternative is to use logging. Not only will you see any
synchronization error messages, but you get to see how the bindings work in
detail. To use logging, you must first initialize the logging system, and then
supply a logger to the binding or binding group::

    from logging import basicConfig, getLogger, DEBUG
    from swingutils.binding import BindingGroup
    from swingutils.beans import JavaBeanSupport, BeanProperty

    class ClassA(JavaBeanSupport):
        property1 = BeanProperty('property1')

    class ClassB(JavaBeanSupport):
        _x = None

        def _getX(self):
            return self._x
        
        def _setX(self, newX):
            oldX = self._x
            self._x = int(newX)
            self.firePropertyChange('x', oldX, newX)

        x = property(_getX, _setX)

    basicConfig(level=DEBUG)
    logger = getLogger(__name__)
    
    object1 = ClassA()
    object2 = ClassB()
    group = BindingGroup(logger=logger)
    group.bind(object1, 'property1', object2, 'x')
    object1.property1 = '123'
    object1.property1 = '0xff'

The obvious error in this is of course that attempting to set
``object1.property`` to a string value that isn't convertable to an integer via
``int()`` causes an exception to be raised in ``ClassB._setX()``. This is what
logging will show for this code:

.. code-block:: none

	DEBUG:__main__:Attribute(property1): adding event listeners (parent=<__main__.ClassA object at 0x3>)
	DEBUG:__main__:Writing source value (None) to target
	DEBUG:__main__:Error writing to target
	Traceback (most recent call last):
	  File "__pyclasspath__/swingutils/binding/__init__$py.class", line 187, in sync
	  File "__pyclasspath__/swingutils/binding/__init__$py.class", line 68, in setValue
	  File "$$binding-writer$$", line 1, in <module>
	  File "__pyclasspath__/swingutils/binding/__init__$py.class", line 37, in __setitem__
	  File "btest.py", line 16, in _setX
	    self._x = int(newX)
	TypeError: int() argument must be a string or a number
	DEBUG:__main__:Attribute(property1): change event triggered
	DEBUG:__main__:Source (property1) changed
	DEBUG:__main__:Writing source value ('123') to target
	DEBUG:__main__:Attribute(property1): change event triggered
	DEBUG:__main__:Source (property1) changed
	DEBUG:__main__:Writing source value ('0xff') to target
	DEBUG:__main__:Error writing to target
	Traceback (most recent call last):
	  File "__pyclasspath__/swingutils/binding/__init__$py.class", line 187, in sync
	  File "__pyclasspath__/swingutils/binding/__init__$py.class", line 68, in setValue
	  File "$$binding-writer$$", line 1, in <module>
	  File "__pyclasspath__/swingutils/binding/__init__$py.class", line 37, in __setitem__
	  File "btest.py", line 16, in _setX
	    self._x = int(newX)
	ValueError: invalid literal for int() with base 10: 0xff

The first error is caused by the initial synchronization (when the value
``None`` is passed to ``object2.x``. Synchronizing the value ``'123'`` works
fine, but ``'0xff'`` causes a ValueError to be raised.
