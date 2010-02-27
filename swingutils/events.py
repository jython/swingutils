from java.util import EventListener
from java.beans import PropertyChangeListener


_wrapperClassMap = {}       # event interface name -> wrapper class

def _createListenerWrapper(eventInterface, event, listener, args, kwargs,
                           removeMethod):
    events = (event,) if isinstance(event, basestring) else event
    assert issubclass(eventInterface, EventListener), \
        'event class must be a subclass of EventListener'
    assert hasattr(listener, '__call__'), 'listener must be callable'
    for event in events:
        assert hasattr(eventInterface, event), \
            '%s has no method named "%s"' % (eventInterface.__name__, event)

    # Create a wrapper class for this event class if one doesn't exist already
    className = eventInterface.__name__
    if not className in _wrapperClassMap:
        wrapperClass = type('%sWrapper' % eventInterface.__name__,
                            (EventListenerWrapper, eventInterface), {})
        _wrapperClassMap[className] = wrapperClass
    else:
        wrapperClass = _wrapperClassMap[className]

    # Create a listener instance and add handleEvent as an instance method
    wrapper = wrapperClass(listener, args, kwargs, removeMethod)
    for event in events:
        setattr(wrapper, event, wrapper.handleEvent)
    return wrapper


class EventListenerWrapper(object):
    def __init__(self, listener, args, kwargs, removeMethod):
        self.listener = listener
        self.args = args
        self.kwargs = kwargs
        self.removeMethod = removeMethod
        self.removeMethodArgs = (self,)

    def handleEvent(self, event):
        self.listener(event, *self.args, **self.kwargs)
    
    def unlisten(self):
        self.removeMethod(*self.removeMethodArgs)


def addEventListener(target, eventInterface, event, listener,
                             *args, **kwargs):
    """
    Adds an event listener to `target`.

    :param target: an object that supports listening to the events of the given
                   type (the add*Listener methods must be inherited from a Java
                   class so that autodetection will work)
    :param eventInterface: the interface that the listener wrapper has to
                           implement (e.g. :class:`java.awt.MouseListener`)
    :param event: name(s) of the event(s) to listen for (e.g. "mouseClicked")
    :param listener: callable that is called with (event, *args, **kwargs)
                     when the event is fired
    :type eventInterface: Java interface
    :type event: string or an iterable of strings
    :type listener: callable
    :return: the listener wrapper that you can use to stop listening to these
             events (with :meth:`~EventListenerWrapper.unlisten`)

    """
    addMethodName = 'add%s' % eventInterface.__name__
    addMethod = getattr(target, addMethodName)
    removeMethodName = 'remove%s' % eventInterface.__name__
    removeMethod = getattr(target, removeMethodName)
    wrapper = _createListenerWrapper(eventInterface, event, listener, args,
                                     kwargs, removeMethod)
    addMethod(wrapper)
    return wrapper

addExplicitEventListener = addEventListener


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
        listener, args, kwargs, target.removePropertyChangeListener)
    wrapper.removeMethodArgs = (property, wrapper)
    target.addPropertyChangeListener(property, wrapper)
    return wrapper
