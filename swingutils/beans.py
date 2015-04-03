"""
This module contains support classes to make your own classes support JavaBeans
compatible property change notifications.

"""
from java.beans import (PropertyChangeSupport, PropertyChangeEvent,
                        IndexedPropertyChangeEvent)


class JavaBeanSupport(object):
    """
    Class that provides support for listening to property change events.

    This class does not provide a Java-compatible interface, so if you need
    that, inherit directly from :class:`java.beans.PropertyChangeSupport`
    instead.

    """
    _changeSupport = None

    def addPropertyChangeListener(self, *args):
        if not self._changeSupport:
            self._changeSupport = PropertyChangeSupport(self)
        self._changeSupport.addPropertyChangeListener(*args)

    def removePropertyChangeListener(self, *args):
        if self._changeSupport:
            self._changeSupport.removePropertyChangeListener(*args)

    def firePropertyChange(self, propertyName, oldValue, newValue):
        if self._changeSupport:
            event = PropertyChangeEvent(self, propertyName, oldValue, newValue)
            self._changeSupport.firePropertyChange(event)

    def fireIndexedPropertyChange(self, propertyName, index, oldValue,
                                  newValue):
        if self._changeSupport:
            event = IndexedPropertyChangeEvent(self, propertyName, oldValue,
                                               newValue, index)
            self._changeSupport.firePropertyChange(event)

    def getPropertyChangeListeners(self, *args):
        if self._changeSupport:
            return self._changeSupport.getPropertyChangeListeners(*args)
        return []

    def hasListeners(self, *args):
        if self._changeSupport:
            return self._changeSupport.hasListeners(*args)
        return False


class AutoChangeNotifier(object):
    """
    Mix-in class that automatically fires property change events for
    public properties (those whose names don't start with an underscore).

    .. note:: If you inherit from this class, make sure that its
              ``__setattr__`` method is not shadowed by another
              ``__setattr__``!

    """
    def __setattr__(self, name, value):
        if name.startswith('_'):
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
    :param initval: Default value for this property. Defaults to ``None``.

    .. seealso:: `How-To Guide for Descriptors
                 <http://users.rcn.com/python/download/Descriptor.htm>`_

    """
    def __init__(self, name, initval=None):
        super(BeanProperty, self).__init__()
        self.name = name
        self.mangled_name = '__beanproperty_%s' % name
        self.defaultValue = initval

    def __get__(self, obj, type_=None):
        return getattr(obj, self.mangled_name, self.defaultValue)

    def __set__(self, obj, value):
        oldValue = self.__get__(obj)
        setattr(obj, self.mangled_name, value)
        obj.firePropertyChange(self.name, oldValue, value)


class MirrorObject(JavaBeanSupport):
    """
    This is a proxy class that provides bound properties support for objects
    that have no such support of their own. Only public properties (ones
    not starting with ``_``) are mirrored.

    """
    __delegate = None

    def __init__(self, delegate=None):
        super(MirrorObject, self).__init__()
        self.__delegate = delegate

    @property
    def _delegate(self):
        return self.__delegate

    @_delegate.setter
    def _delegate(self, newDelegate):
        oldDelegate = self.__delegate
        self.__delegate = newDelegate
        self.firePropertyChange('_delegate', oldDelegate, newDelegate)

        # Collect public property names from both old and new
        propertyNames = set()
        for attr in set(dir(oldDelegate) + dir(newDelegate)):
            if not attr.startswith('_') and self.hasListeners(attr):
                propertyNames.add(attr)

        # Fire a property change event for each attribute
        for attr in propertyNames:
            try:
                oldValue = getattr(oldDelegate, attr, None)
                newValue = getattr(newDelegate, attr, None)
                self.firePropertyChange(attr, oldValue, newValue)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                pass

    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        return getattr(self._delegate, name, None)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            oldValue = getattr(self._delegate, name, None)
            setattr(self._delegate, name, value)
            self.firePropertyChange(name, oldValue, value)

    def __nonzero__(self):
        return self._delegate is not None
