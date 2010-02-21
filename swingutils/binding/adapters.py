from swingutils.events import addPropertyListener, addExplicitEventListener


class AdapterRegistry(dict):
    def register(self, cls):
        try:
            classname = cls.__classname__
        except AttributeError:
            raise AttributeError(u'Adapter class %s is missing the '
                                 u'__classname__ attribute' %
                                 self._getClassName(cls))

        self[classname] = cls

    @staticmethod
    def _getClassName(cls):
        if cls.__module__ not in ('__builtin__', '__main__'):
            return u'%s.%s' % (cls.__module__, cls.__name__)
        return cls.__name__

    def get(self, obj, options):
        # Gather a list of class names from the inheritance chain
        classnames = []
        cls = obj.__class__
        while cls:
            classnames.append(self._getClassName(cls))
            cls = getattr(cls, 'superclass', None)

        # Find the nearest matching adapter for this class
        bestMatch = BaseAdapter
        bestMatchIndex = None
        for key, value in self.iteritems():
            if key in classnames:
                index = classnames.index(key)
                if not bestMatchIndex or bestMatchIndex > index:
                    bestMatch = value
                    bestMatchIndex = index
                if index == 0:
                    break

        # Instantiate the adapter with the given options
        return bestMatch(**options)

registry = AdapterRegistry()


class BaseAdapter(object):
    listener = None

    def addListener(self, obj, property, callback):
        self.listener = addPropertyListener(obj, property, callback)

    def removeListener(self, obj, property):
        if self.listener:
            self.listener.unlisten()
            del self.listener


@registry.register
class AbstractButtonAdapter(BaseAdapter):
    __classname__ = 'javax.swing.AbstractButton'

    def addListener(self, obj, property, callback):
        if property == 'selected':
            from java.awt.event import ItemListener
            self.itemlistener = addExplicitEventListener(obj, ItemListener,
                'itemStateChanged', callback)
        else:
            BaseAdapter.addListener(self, obj, property, callback)


@registry.register
class JTextComponentAdapter(BaseAdapter):
    __classname__ = 'javax.swing.text.JTextComponent'
    
    docListener = None

    def __init__(self, onFocusLost=False):
        """
        :param onFocusLost: ``True`` if the binding should be synchronized
            when the field loses focus, ``False`` to synchronize whenever the
            associated document is changed

        """
        self.onFocusLost = onFocusLost

    def addListener(self, obj, property, callback):
        if property == 'text':
            if self.onFocusLost:
                self.addFocusListener(obj, callback)
            else:
                # Track changes to both JTextComponent.document and the
                # document itself
                self.listener = addPropertyListener(obj, 'document',
                    self.documentChanged, obj, callback)
                self.addDocumentListener(obj.document, callback)
        else:
            BaseAdapter.addListener(self, obj, property, callback)

    def addFocusListener(self, obj, callback):
        from java.awt.event import FocusListener
        self.listener = addExplicitEventListener(obj, FocusListener,
                                                 'focusLost', callback)

    def addDocumentListener(self, document, callback):
        from javax.swing.event import DocumentListener
        for event in (u'changedUpdate', u'insertUpdate', u'removeUpdate'):
            self.docListener = addExplicitEventListener(document,
                DocumentListener, event, callback)

    def documentChanged(self, event, obj, callback):
        self.listener.unlisten()
        self.addDocumentListener(obj, event.newValue)
        callback()

    def removeListener(self, obj, property):
        BaseAdapter.removeListener(self, obj, property)
        if self.docListener:
            self.docListener.unlisten()
            del self.docListener
