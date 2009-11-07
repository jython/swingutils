"""
This module contains mix-in classes to make your classes support JavaBeans
compatible property change notifications.

"""
from java.beans import PropertyChangeListener, PropertyChangeEvent


class _PropertyChangeWrapper(PropertyChangeListener):
    def __init__(self, source, listener, property):
        self.source = source
        self.listener = listener
        self.property = property

    def __call__(self, oldValue, newValue, property=None):
        e = PropertyChangeEvent(self.source, property or self.property,
                                oldValue, newValue)
        self.listener.propertyChange(e)

    def __eq__(self, obj):
        return obj in (self, self.listener)


class JavaBeanSupport(object):
    """Class that provides support for listening to property change events"""

    _listeners = None

    #
    # Java-style API
    #

    def addPropertyChangeListener(self, *args):
        if len(args) == 2:
            property, listener = args
        elif len(args) == 1:
            property, listener = None, args[0]
        else:
            raise TypeError('addPropertyChangeListener expected 1-2 '
                            'arguments, got 0')
        assert isinstance(listener, PropertyChangeListener)
        wrapper = _PropertyChangeWrapper(self, listener, property)
        self.addPropertyListener(wrapper, property)

    def removePropertyChangeListener(self, *args):
        if len(args) == 2:
            property, listener = args
        elif len(args) == 1:
            property, listener = None, args[0]
        else:
            raise TypeError('removePropertyChangeListener expected 1-2 '
                            'arguments, got 0')
        assert isinstance(listener, PropertyChangeListener)
        
        if self._listeners:
            try:
                for wrapper in self._listeners[property]:
                    if (isinstance(wrapper, _PropertyChangeWrapper) and
                        wrapper.listener == listener):
                        self._listeners[property].remove(wrapper)
                        return
            except KeyError:
                pass

    #
    # Python API
    #

    def firePropertyChange(self, property, oldValue, newValue):
        if self._listeners and oldValue != newValue:
            if property in self._listeners:
                for listener, args, kwargs in self._listeners[property]:
                    listener(oldValue, newValue, *args, **kwargs)
            if None in self._listeners:
                for listener, args, kwargs in self._listeners[None]:
                    listener(oldValue, newValue, property, *args, **kwargs)

    def addPropertyListener(self, listener, property=None, *args, **kwargs):
        """
        Adds a callback that is called when the given property has changed.
        A listener can either listen to changes in a specific property,
        or all properties (by supplying `None` as the property name).
        Any extra positional and keyword arguments are passed on to the
        listener.

        The listener is called with (oldValue, newValue, *args, **kwargs)
        if the property name was defined, and (oldValue, newValue, property,
        *args, **kwargs) if it's set to listen to all property changes.

        :type listener: function or any callable
        :param property: name of the property, or None to listen to all
                         property changes

        """
        if not hasattr(listener, '__call__'):
            raise TypeError('listener must be callable')

        if self._listeners is None:
            self._listeners = {}

        if not property in self._listeners:
            self._listeners[property] = []
        self._listeners[property].append((listener, args, kwargs))

    def removePropertyListener(self, listener, property=None):
        if self._listeners and property in self._listeners:
            for i, (listener_, args, kwargs) in \
                enumerate(self._listeners[property]):
                if listener_ == listener:
                    del self._listeners[property][i]
                    return


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
