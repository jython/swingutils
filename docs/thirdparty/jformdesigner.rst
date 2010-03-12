JFormDesigner support
=====================

This module allows developers to easily load forms created with
`JFormDesigner <http://www.jformdesigner.com/>`_. JFormDesigner is a
commercial visual design tool for Swing based user interfaces.

Requirements
------------

For form loading to work, you must have the JFormDesigner form loader library,
``jfd-loader.jar``, in your class path. The
`Jython book <http://jythonpodcast.hostjava.net/jythonbook/en/.99/appendixB.html#using-the-classpath-steve-langer>`_
has some instructions on how to accomplish that.

Loading forms
-------------

The :class:`~swingutils.thirdparty.jformdesigner.FormWrapper` class and its
subclasses, :class:`~swingutils.thirdparty.jformdesigner.PanelWrapper` and
:class:`~swingutils.thirdparty.jformdesigner.WindowWrapper`, provide you with
the means to load and use your .jfd forms. In typical use cases, you normally
want to use either of those subclasses. PanelWrapper is meant to load forms
that have a JPanel as their top element, while WindowWrapper is meant for
forms with a window as their top element (which includes JFrame, JDialog etc).

Example (loading a JFrame based form)::

    from swingutils.thirdparty.jformdesigner import WindowWrapper
    
    class MainFrame(WindowWrapper):
        def __init__(self):
            WindowWrapper.__init__(self, 'someform.jfd')

You don't necessarily have to subclass the wrappers, but it's often convenient
to do so. If you omit the form name, it will determine it from the class name
by appending ".jfd" to its name. If you do this, you'll obviously have to
subclass one of the wrapper classes. The form file is loaded with the standard
Java resource loading API, so it can be included in a .jar file.

.. note:: Don't define event handlers in your forms, as they will not work with
          the current Jython version.

Accessing form components
-------------------------

All form components are accessible as attributes of the form wrapper.
This was implemented by defining a ``__getattr__`` method that looks up the
component name in case an actual attribute is not found by that name.

The top level component can be accessed as ``window`` in
class:`~swingutils.thirdparty.jformdesigner.WindowWrapper`, and ``panel``
in :class:`~swingutils.thirdparty.jformdesigner.PanelWrapper`.
