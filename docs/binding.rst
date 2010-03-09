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
automatically copied to object2.anotherproperty.

The only requirement for this to work is that object1 has support for
`bound properties <http://java.sun.com/docs/books/tutorial/javabeans/properties/bound.html>`_.
With two way binding, object2 also needs to support bound properties.
See the :ref:`Beans section <beans>` for more information on how to accomplish
that.

How it works
------------

To understand how to properly use Swingutils Binding, you should get acquainted
with some of its basic concepts.

Binding groups
""""""""""""""

A binding group is a container for a number of bindings. The purpose of storing
bindings in groups is twofold. First, it enables you to manually synchronize
a number of bindings at once with a simple method call. Second, it's a
convenient way to set default options for bindings.

.. seealso:: :class:`swingutils.binding.BindingGroup`

Bindings
""""""""

A binding is an object that handles the synchronization of two properties.
It contains exactly two binding expressions, one for the source, one for the
target. Developers usually don't have to deal with these directly.

.. seealso:: :class:`swingutils.binding.Binding`

Binding expressions
"""""""""""""""""""

A binding expression is the container for the actual expression. When it is
`bound` (by the Binding object that owns it), it parses the expression into one
or more `binding chains` (explained below). In addition, the expression object
implements read/write operations for the expression.

.. seealso:: :class:`swingutils.binding.BindingExpression`

Binding chains
""""""""""""""

A binding chain is a linked list of nodes created from some part of the
binding expression they belong to. Consider the following binding expression::

	expr = BindingExpression(obj, 'employer.name.startswith(prefix) and name == "Alex"')

The source expression contains three chains, which you can print with ``group.dump()``::

General Binding options
-----------------------

These are options that can be passed as keyword arguments to the constructors
of :class:`~swingutils.binding.BindingGroup`, :class:`~swingutils.binding.Binding`
and :class:`~swingutils.binding.BindingExpression`.
Options are propagated from group to a binding to a binding expression.

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

The following table lists the options for all built-in adapters.

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

Technical details
-----------------

Reading and writing
"""""""""""""""""""

Reading from binding expressions is implemented so that the source code of the
expression is compiled to a code object the first time the read operation is
invoked. The resulting code object is then evaluated with a dictionary-like
object that gives it access to the variables the expressions's root object and
any extra variables found in the ``vars`` dict in options.

Writing is implemented much like reading, except that the source code is
compiled after appending ``=___binding_value`` to the source. The resulting
code is then executed with the globals set to the root object's variables plus
the extra variables from ``options['vars']``.

