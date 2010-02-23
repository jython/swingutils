from swingutils.events import addPropertyListener, addExplicitEventListener


class AdapterRegistry(object):
    def __init__(self):
        self._propertyAdapters = {}
        self._listAdapters = {}
    
    def _registerAdapter(self, cls, adapters):
        try:
            classname = cls.__classname__
        except AttributeError:
            raise AttributeError(u'Adapter class %s is missing the '
                                 u'__classname__ attribute' %
                                 self._getClassName(cls))

        adapters[classname] = cls
        return cls
    
    def registerPropertyAdapter(self, cls):
        return self._registerAdapter(cls, self._propertyAdapters)

    def registerListAdapter(self, cls):
        return self._registerAdapter(cls, self._listAdapters)

    @staticmethod
    def _getClassName(cls):
        if cls.__module__ not in ('__builtin__', '__main__'):
            return u'%s.%s' % (cls.__module__, cls.__name__)
        return cls.__name__

    def _getAdapter(self, candidates, default, obj, options):
        # Gather a list of class names from the inheritance chain
        classnames = []
        cls = obj.__class__
        while cls:
            classnames.append(self._getClassName(cls))
            cls = getattr(cls, 'superclass', None)

        # Find the nearest matching adapter for this class
        bestMatch = default
        bestMatchIndex = None
        for key, value in candidates.iteritems():
            if key in classnames:
                index = classnames.index(key)
                if not bestMatchIndex or bestMatchIndex > index:
                    bestMatch = value
                    bestMatchIndex = index
                if index == 0:
                    break

        # Instantiate the adapter with the given options
        return bestMatch(options) if bestMatch else None

    def getPropertyAdapter(self, obj, options):
        return self._getAdapter(self._propertyAdapters, BasePropertyAdapter,
                                obj, options)

    def getListAdapter(self, obj, options):
        return self._getAdapter(self._listAdapters, None, obj, options)

registry = AdapterRegistry()


class BasePropertyAdapter(object):
    listener = None
    
    def __init__(self, options):
        pass

    def addListener(self, obj, property, callback, *args, **kwargs):
        self.listener = addPropertyListener(obj, property, callback, *args,
                                            **kwargs)

    def removeListener(self):
        if self.listener is not None:
            self.listener.unlisten()
            del self.listener


@registry.registerPropertyAdapter
class AbstractButtonAdapter(BasePropertyAdapter):
    __classname__ = 'javax.swing.AbstractButton'

    def addListener(self, obj, property, callback, *args, **kwargs):
        if property == 'selected':
            from java.awt.event import ItemListener
            self.itemlistener = addExplicitEventListener(obj, ItemListener,
                'itemStateChanged', callback, *args, **kwargs)
        else:
            BasePropertyAdapter.addListener(self, obj, property, callback,
                                            *args, **kwargs)


@registry.registerPropertyAdapter
class JTextComponentAdapter(BasePropertyAdapter):
    """
    :ivar onFocusLost: ``True`` if the binding should be synchronized
        when the field loses focus, ``False`` to synchronize whenever the
        associated document is changed. Default is ``False``.

    """
    __classname__ = 'javax.swing.text.JTextComponent'
    
    docListener = None

    def __init__(self, options):
        self.onFocusLost = options.get('onFocusLost', False)

    def addListener(self, obj, property, callback, *args, **kwargs):
        if property == 'text':
            if self.onFocusLost:
                self.addFocusListener(obj, callback, *args, **kwargs)
            else:
                # Track changes to both JTextComponent.document and the
                # document itself
                self.listener = addPropertyListener(obj, 'document',
                    self.documentChanged, obj, callback)
                self.addDocumentListener(obj.document, callback)
        else:
            BasePropertyAdapter.addListener(self, obj, property, callback,
                                            *args, **kwargs)

    def addFocusListener(self, obj, callback, *args, **kwargs):
        from java.awt.event import FocusListener
        self.listener = addExplicitEventListener(obj, FocusListener,
            'focusLost', callback, *args, **kwargs)

    def addDocumentListener(self, document, callback, *args, **kwargs):
        from javax.swing.event import DocumentListener
        for event in (u'changedUpdate', u'insertUpdate', u'removeUpdate'):
            self.docListener = addExplicitEventListener(document,
                DocumentListener, event, callback, *args, **kwargs)

    def documentChanged(self, event, obj, callback, *args, **kwargs):
        self.listener.unlisten()
        self.addDocumentListener(obj, event.newValue)
        callback(*args, **kwargs)

    def removeListener(self):
        BasePropertyAdapter.removeListener(self)
        if self.docListener is not None:
            self.docListener.unlisten()
            del self.docListener


@registry.registerPropertyAdapter
class JListAdapter(BasePropertyAdapter):
    """
    :ivar ignoreAdjusting: ``True`` if the callback should only be called
        when the selection list has finished adjusting.
        Default is ``True``.

    """
    __classname__ = 'javax.swing.JList'
    
    def __init__(self, options):
        self.ignoreAdjusting = options.get('ignoreAdjusting', True)
