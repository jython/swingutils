Binding
=======

Binding is a mechanism for keeping properties between two objects synchronized.
This can be very useful for providing data to UI components like form fields,
lists, tables etc., but it is by no means limited to that.

General Binding options
-----------------------

These are options that can be passed as keyword arguments to
:class:`~swingutils.binding.BindingGroup`, :class:`~swingutils.binding.Binding`
and :class:`~swingutils.binding.BindingExpression`.
Options are propagated from group to a binding to a binding expression.

In addition to these, various adapters have their own options. See the
adapters section for specifics.

============    ===========================================================
Option          Definition
============    ===========================================================
mode            Synchronization mode (integer). Available options are:
                 * MANUAL (0): No automatic synchronization
                 * ONEWAY (1): Copy source to target when source changes
                 * TWOWAY (2): Like ONEWAY but also copy target to source
                   when target changes

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
============    ===========================================================

Adapters
--------

Adapters are helper classes that Binding uses automatically when needed to
facilitate binding to properties that don't report of changes in their values
like normal JavaBeans properties. An example of this would be the `text`
property in the commonly used :class:`javax.swing.JTextField` class. Instead
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
