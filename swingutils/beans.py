"""
This module contains mix-in classes to make your classes support JavaBeans
compatible property change notifications.

"""

from java.beans import PropertyChangeSupport, PropertyChangeListener


class _PropertyChangeWrapper(PropertyChangeListener):
    def __init__(self, listener, all_properties, args, kwargs):
        self.listener = listener
        self.all_properties = all_properties
        self.args = args
        self.kwargs = kwargs

    def propertyChange(self, evt):
        if self.all_properties:
            self.listener(evt.propertyName, evt.oldValue, evt.newValue,
                          *self.args, **self.kwargs)
        else:
            self.listener(evt.oldValue, evt.newValue, *self.args,
                          **self.kwargs)


class JavaBeanSupport(object):
    """Class that provides support for listening to property change events"""

    _changeSupport = None

    def addPropertyChangeListener(self, propertyName, listener=None):
        if not self._changeSupport:
            self._changeSupport = PropertyChangeSupport(self)

        if listener is None:
            propertyName, listener = None, propertyName

        if propertyName:
            self._changeSupport.addPropertyChangeListener(propertyName,
                                                          listener)
        else:
            self._changeSupport.addPropertyChangeListener(listener)

    def removePropertyChangeListener(self, propertyName, listener=None):
        if self._changeSupport:
            if listener is None:
                propertyName, listener = None, propertyName

            if propertyName:
                self._changeSupport.removePropertyChangeListener(propertyName,
                                                                 listener)
            else:
                self._changeSupport.removePropertyChangeListener(listener)

    def _firePropertyChange(self, propertyName, oldValue, newValue):
        if self._changeSupport:
            self._changeSupport.firePropertyChange(propertyName, oldValue,
                                                   newValue)

    def addPropertyListener(self, listener, property=None, *args, **kwargs):
        """
        Python-style method for adding property listeners.
        
        :param listener: callable that is called with (oldValue, newValue,
                         **args, **kwargs) if property was defined, and
                         (property, oldValue, newValue, *args, **kwargs) if
                         property was None.

        """
        if not hasattr(listener, '__call__'):
            raise TypeError('listener must be callable')
        wrapper = _PropertyChangeWrapper(listener, property is None, args,
                                         kwargs)
        self.addPropertyChangeListener(property, wrapper)
        return wrapper

    def removePropertyListener(self, listener, property=None):
        self.removePropertyChangeListener(property, listener)


class AutoChangeNotifier(JavaBeanSupport):
    """Automatically fires property change events for public properties"""

    def __setattr__(self, name, value):
        if not self._changeSupport or name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            oldValue = getattr(self, name)
            object.__setattr__(self, name, value)
            newValue = getattr(self, name)
            self._firePropertyChange(name, oldValue, newValue)
