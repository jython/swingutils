.. _beans:

JavaBeans support
=================

This module contains classes that you can use to add support for `bound
properties <http://java.sun.com/docs/books/tutorial/javabeans/properties/bound.html>`_
in your classes. This includes being able to add/remove property change
listeners, and firing property change events when the attribute values change.

There are two ways to do this:

* Inherit from a class that has the necessary ``addPropertyChangeListener`` and
  ``removePropertyChangeListener`` methods (like a Swing component, or
  :class:`~swingutils.beans.JavaBeanSupport`) and add the properties you want
  to fire change events as :class:`swingutils.beans.BeanProperty` attributes

  OR

* Inherit from the :class:`~swingutils.beans.AutoChangeNotifier` mix-in class

Both approaches have their pros and cons, which are detailed below.

BeanProperty
------------

This is a `descriptor class <http://docs.python.org/reference/datamodel.html#descriptors>`_
that should be installed as a class attribute in a new-style object (one that
inherits from ``object``). It handles getting and setting the value, and fires
a property change event when the value is set. It requires that the containing
class supports property change events (via the add/remove methods mentioned
above).

Example::

    from swingutils.beans import JavaBeanSupport, BeanProperty

    class JustSomeBean(JavaBeanSupport):
        foo = BeanProperty('foo')
        bar = BeanProperty('bar', 'the initial value')
    
    bean = JustSomeBean()
    bean.bar = 'the next value'     # Would fire a property change event

**Pros:**

- Fine grained, can be set up one property at a time
- Plays well together with superclasses that already support bound properties

**Cons:**

- Cumbersome if you want to make all properties in a class fire property
  change events

AutoChangeNotifier
------------------

This is a mix-in class that works by providing a special method,
``__setattr__``, that catches any attempts to set the value of an attribute.
It stores the old value, sets the new attribute value, and then fires a
property change event. Private and protected attributes (names starting with
``_``) are excluded from this behavior.

Example::

    from swingutils.beans import AutoChangeNotifier

    class JustSomeBean(AutoChangeNotifier):
        foo = None
        bar = 'the initial value'
        
    bean = JustSomeBean()
    bean.bar = 'the next value'     # Would fire a property change event

**Pros:**

- Easy to set up, just inherit from it and you're good to go
- Works for all public properties without extra configuration

**Cons:**

- May conflict with an existing ``__setitem__`` method
- Coarse grained -- can't choose which public attributes to fire events for
