from java.beans import PropertyChangeListener


class PropertyListenerWrapper(PropertyChangeListener):
    def __init__(self, listener, args, kwargs):
        self.listener = listener
        self.args = args
        self.kwargs = kwargs
    
    def propertyChange(self, event):
        self.listener(event, *self.args, **self.kwargs)


def addPropertyListener(target, property, listener, *args, **kwargs):
    """
    Adds a callback that is called when the given property has changed.
    A listener can either listen to changes in a specific property,
    or all properties (by supplying `None` as the property name).
    The listener is called with (event, *args, **kwargs).

    :param target: the object whose property will be listened to
    :param property: name of the property, or None to listen to all
                     property changes
    :type listener: function or any callable
    :rtype: :class:`PropertyListenerWrapper`

    """
    assert hasattr(listener, '__call__'), 'listener must be callable'
    wrapper = PropertyListenerWrapper(listener, args, kwargs)
    target.addPropertyChangeListener(property, wrapper)
    return wrapper
