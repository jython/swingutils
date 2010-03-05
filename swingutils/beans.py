"""
This module contains support classes to make your own classes support JavaBeans
compatible property change notifications.

"""
from java.beans import PropertyChangeListener, PropertyChangeEvent


class JavaBeanSupport(object):
    """
    Class that provides support for listening to property change events.

    .. note:: These added methods are **not** visible to Java, so classes
              inheriting from this class **cannot** be used as regular
              JavaBeans from Java code.

    """
    _listeners = None

    def addPropertyChangeListener(self, *args):
        if len(args) == 2:
            property, listener = args
        elif len(args) == 1:
            property, listener = None, args[0]
        else:
            raise TypeError('addPropertyChangeListener expected 1-2 '
                            'arguments, got %d' % len(args))
        assert isinstance(listener, PropertyChangeListener)

        if self._listeners is None:
            self._listeners = {}

        if not property in self._listeners:
            self._listeners[property] = [listener]
        else:
            self._listeners[property].append(listener)

    def removePropertyChangeListener(self, *args):
        if len(args) == 2:
            property, listener = args
        elif len(args) == 1:
            property, listener = None, args[0]
        else:
            raise TypeError('removePropertyChangeListener expected 1-2 '
                            'arguments, got %d' % len(args))
        assert isinstance(listener, PropertyChangeListener)

        if (self._listeners and property in self._listeners and
            listener in self._listeners[property]):
            self._listeners[property].remove(listener)

    def firePropertyChange(self, property, oldValue, newValue):
        event = PropertyChangeEvent(self, property, oldValue, newValue)
        if self._listeners and oldValue != newValue:
            if property in self._listeners:
                for listener in self._listeners[property]:
                    listener.propertyChange(event)
            if None in self._listeners:
                for listener in self._listeners[None]:
                    listener.propertyChange(event)


class AutoChangeNotifier(JavaBeanSupport):
    """
    Mix-in class that automatically fires property change events for
    public properties (those whose names don't start with an underscore).
    
    .. note:: If you inherit from this class, make sure that its
              ``__setattr__`` method is not shadowed by another
              ``__setattr__``!

    """
    def __setattr__(self, name, value):
        if not self._listeners or name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            oldValue = getattr(self, name, None)
            object.__setattr__(self, name, value)
            newValue = getattr(self, name)
            self.firePropertyChange(name, oldValue, newValue)


class BeanProperty(object):
    """
    Descriptor class that fires a property change event from the host object
    when the value is updated. The containing class must have bean property
    support, either inherited from a Java class or from
    :class:`~JavaBeanSupport`.

    Example::

        class Foo(JavaBeanSupport):
            myAttribute = BeanProperty('myAttribute')

    :param name: Attribute name of the bean property. This MUST be the
                 same name as the created attribute, as it can't be
                 reliably obtained any other way.
    :param initval: Initial value for this property. Defaults to ``None``.

    .. seealso:: `How-To Guide for Descriptors <http://users.rcn.com/python/download/Descriptor.htm>`_

    """
    def __init__(self, name, initval=None):
        self.name = name
        self.value = initval

    def __get__(self, obj, type_=None):
        return self.value

    def __set__(self, obj, value):
        oldValue = self.value
        self.value = value
        obj.firePropertyChange(self.name, oldValue, value)
