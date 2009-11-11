from java.util import EventListener
from java.beans import PropertyChangeListener


_wrapperClassMap = {}       # event interface name -> wrapper class

def _findListenerAddMethods(target):
    """
    Finds the add*Listener methods in `target`.

    """
    for attrName in dir(target):
        if attrName.startswith('add') and attrName.endswith('Listener'):
            attr = getattr(target, attrName)
            if hasattr(attr, 'argslist'):
                yield attr


def _findEventInterface(target, event):
    """
    Finds the event interface from target's method that contains the `event`
    method.

    """
    for method in _findListenerAddMethods(target):
        for variation in method.argslist:
            if len(variation.args) == 1:
                class_ = variation.args[0]
                if (issubclass(class_, EventListener) and
                    hasattr(class_, event)):
                    return class_


def _createListenerWrapper(eventInterface, event, listener, args, kwargs):
    assert issubclass(eventInterface, EventListener), \
        'event class must be a subclass of EventListener'
    assert hasattr(eventInterface, event), \
        '%s has no method named "%s"' % (eventInterface.__name__, event)
    assert hasattr(listener, '__call__'), 'listener must be callable'

    # Create a wrapper class for this event class
    className = eventInterface.__name__
    if not className in _wrapperClassMap:
        wrapperClass = type('%sWrapper' % eventInterface.__name__,
                            (EventListenerWrapper, eventInterface), {})
        _wrapperClassMap[className] = wrapperClass
    else:
        wrapperClass = _wrapperClassMap[className]

    # Create a listener instance and add handleEvent as an instance method
    wrapper = wrapperClass(listener, args, kwargs)
    setattr(wrapper, event, wrapper.handleEvent)
    return wrapper


class EventListenerWrapper(object):
    def __init__(self, listener, args, kwargs):
        self.listener = listener
        self.args = args
        self.kwargs = kwargs

    def handleEvent(self, event):
        self.listener(event, *self.args, **self.kwargs)


def addExplicitEventListener(target, eventInterface, event, listener,
                             *args, **kwargs):
    """
    Adds an event listener to `target`.

    :param target: the object to add the event listener to
    :param eventInterface: the interface that the listener wrapper has to
                           implement (e.g. java.awt.MouseListener)
    :param event: name of the event to listen for (e.g. "mouseClicked"
    :param listener: callable that is called with (event, *args, **kwargs)
                     when the event is fired
    :type target: any type that supports listening to the events of the given
                  type (the add*Listener methods must be inherited from a Java
                  class so that autodetection will work)
    :type eventInterface: Java class (interface)
    :type event: string
    :type listener: callable
    :return: the listener wrapper that you can use to stop listening to these
             events (with obj.removeXListener())

    """
    wrapper = _createListenerWrapper(eventInterface, event, listener, args,
                                     kwargs)
    addMethodName = 'add%s' % eventInterface.__name__
    addMethod = getattr(target, addMethodName)
    addMethod(wrapper)
    return wrapper


def addEventListener(target, event, listener, *args, **kwargs):
    """
    Adds an event listener to `target`.

    The appropriate event listener interface is automatically guessed from
    the name of the event and the declared Java methods on the target type.
    
    .. note:: This method is on the order of 200 times slower than
    :func:addExplicitEventListener!

    :param target: the object to add the event listener to
    :param event: name of the event to listen for (e.g. "mouseClicked"
    :param listener: callable that is called with (event, *args, **kwargs)
                     when the event is fired
    :type target: any type that supports listening to the events of the given
                  type (the add*Listener methods must be inherited from a Java
                  class so that autodetection will work)
    :type event: string
    :type listener: callable
    :return: the listener wrapper that you can use to stop listening to these
             events (with obj.removeXListener())

    """
    eventInterface = _findEventInterface(target, event)
    return addExplicitEventListener(target, eventInterface, event, listener,
                                    *args, **kwargs)


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
    :return: the listener wrapper that you can use to stop listening to these
             events (with obj.removePropertyChangeListener())

    """
    wrapper = _createListenerWrapper(PropertyChangeListener, 'propertyChange',
                                     listener, args, kwargs)
    target.addPropertyChangeListener(property, wrapper)
    return wrapper
