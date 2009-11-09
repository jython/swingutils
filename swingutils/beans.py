"""
This module contains mix-in classes to make your classes support JavaBeans
compatible property change notifications.

"""
from java.beans import PropertyChangeListener, PropertyChangeEvent


class JavaBeanSupport(object):
    """Class that provides support for listening to property change events"""

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
    """Automatically fires property change events for public properties"""

    def __setattr__(self, name, value):
        if not self._listeners or name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            oldValue = getattr(self, name)
            object.__setattr__(self, name, value)
            newValue = getattr(self, name)
            self.firePropertyChange(name, oldValue, newValue)
