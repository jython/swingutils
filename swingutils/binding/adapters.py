from swingutils.events import addPropertyListener, addExplicitEventListener


class AdapterRegistry(object):
    def __init__(self):
        self.propertyAdapters = {}
        self.listAdapters = {}

    def _getClassNames(self, cls, names=None, level=0):
        """Retrieves the class name of `cls` and names of its superclasses."""

        if names is None:
            names = []
        clsname = u'%s.%s' % (cls.__module__, cls.__name__)

        # Skip proxy classes
        if not u'$' in clsname:
            names.append(clsname)
        for basecls in cls.__bases__:
            self._getClassNames(basecls, names, level + 1)
        return names

    def registerPropertyAdapter(self, cls):
        properties = cls.__targetproperty__
        if isinstance(cls.__targetproperty__, basestring):
            properties = (cls.__targetproperty__,)

        for property in properties:
            key = (cls.__targetclass__, property)
            self.propertyAdapters[key] = cls

        return cls

    def registerListAdapter(self, cls):
        key = cls.__targetclass__
        self.listAdapters[key] = cls
        return cls

    def getPropertyAdapter(self, obj, property, options):
        # Gather a list of class names from the inheritance chain
        targetClassNames = self._getClassNames(obj.__class__)
        targetClassNames.sort()

        # Find the nearest matching adapter for this class
        adapterClass = DefaultPropertyAdapter
        for className in targetClassNames:
            key = (className, property)
            if key in self.propertyAdapters:
                adapterClass = self.propertyAdapters[key]
                break

        return adapterClass(property, options)

    def getListAdapter(self, obj, options):
        # Gather a list of class names from the inheritance chain
        targetClassNames = self._getClassNames(obj.__class__)
        targetClassNames.sort()

        # Find the nearest matching adapter for this class
        adapterClass = None
        for className in targetClassNames:
            if className in self.listAdapters:
                adapterClass = self.listAdapters[className]
                break

        if adapterClass:
            return adapterClass(options)

registry = AdapterRegistry()


class BaseAdapter(object):
    listener = None

    def removeListeners(self):
        if self.listener is not None:
            self.listener.unlisten()
            del self.listener


class DefaultPropertyAdapter(BaseAdapter):
    def __init__(self, property, options):
        self.property = property

    def addListeners(self, obj, callback, *args, **kwargs):
        self.listener = addPropertyListener(obj, self.property, callback,
                                            *args, **kwargs)


@registry.registerPropertyAdapter
class ItemSelectableAdapter(DefaultPropertyAdapter):
    __targetclass__ = 'java.awt.ItemSelectable'
    __targetproperty__ = 'selected'

    def addListeners(self, obj, callback, *args, **kwargs):
        from java.awt.event import ItemListener
        self.listener = addExplicitEventListener(obj, ItemListener,
            'itemStateChanged', callback, *args, **kwargs)


@registry.registerPropertyAdapter
class JTextComponentAdapter(DefaultPropertyAdapter):
    """
    Adapter for text components like JTextField, JFormattedTextField and
    JTextArea.
    
    :ivar onFocusLost: ``True`` if the binding should be synchronized
        when the field loses focus, ``False`` to synchronize whenever the
        associated document is changed. Default is ``False``.

    """
    __targetclass__ = 'javax.swing.text.JTextComponent'
    __targetproperty__ = 'text'

    def __init__(self, property, options):
        self.onFocusLost = options.get('onFocusLost', False)
        self.docListeners = []

    def addListeners(self, obj, callback, *args, **kwargs):
        if self.onFocusLost:
            self.addFocusListener(obj, callback, *args, **kwargs)
        else:
            # Track changes to both JTextComponent.document and the
            # document itself
            self.listener = addPropertyListener(obj, 'document',
                self.documentChanged, obj, callback, *args, **kwargs)
            self.addDocumentListeners(obj.document, callback, *args,
                                      **kwargs)

    def addFocusListener(self, obj, callback, *args, **kwargs):
        from java.awt.event import FocusListener
        self.listener = addExplicitEventListener(obj, FocusListener,
            'focusLost', callback, *args, **kwargs)

    def addDocumentListeners(self, document, callback, *args, **kwargs):
        from javax.swing.event import DocumentListener
        for event in (u'changedUpdate', u'insertUpdate', u'removeUpdate'):
            listener = addExplicitEventListener(document, DocumentListener,
                event, callback, *args, **kwargs)
            self.docListeners.append(listener)

    def removeListeners(self):
        DefaultPropertyAdapter.removeListeners(self)
        for listener in self.docListeners:
            listener.unlisten()
        del self.docListeners[:]

    def documentChanged(self, event, obj, callback, *args, **kwargs):
        self.removeListeners()
        self.addListeners(obj, callback, *args, **kwargs)
        callback(*args, **kwargs)


@registry.registerPropertyAdapter
class JListAdapter(DefaultPropertyAdapter):
    """
    Adapter for :class:`javax.swing.JList`.

    :ivar ignoreAdjusting: ``True`` if the callback should only be called
        when the selection list has finished adjusting.
        Default is ``True``.

    """
    __targetclass__ = 'javax.swing.JList'
    __targetproperty__ = ('selectedValue', 'selectedIndex', 'selectedIndices',
                          'leadSelectionIndex', 'anchorSelectionIndex',
                          'maxSelectionIndex', 'minSelectionIndex')

    selectionModeListener = None

    def __init__(self, property, options):
        DefaultPropertyAdapter.__init__(self, property, options)
        self.ignoreAdjusting = options.get('ignoreAdjusting', True)

    def addListeners(self, obj, callback, *args, **kwargs):
        from javax.swing.event import ListSelectionListener
        self.listener = addPropertyListener(obj, 'selectionModel',
            self.selectionModelChanged, obj, callback, *args, **kwargs)
        self.selectionModeListener = addExplicitEventListener(obj,
            ListSelectionListener, 'valueChanged', callback, *args, **kwargs)

    def removeListeners(self):
        DefaultPropertyAdapter.removeListeners(self)
        if self.selectionModeListener:
            self.selectionModeListener.unlisten()
            del self.selectionModeListener

    def selectionModelChanged(self, event, obj, callback, *args, **kwargs):
        self.removeListeners()
        self.addListeners(obj, callback, *args, **kwargs)
        callback(*args, **kwargs)

    def selectionChanged(self, event, callback, *args, **kwargs):
        if not event.valueIsAdjusting or not self.ignoreAdjusting:
            callback(*args, **kwargs)


@registry.registerPropertyAdapter
class JComboBoxAdapter(DefaultPropertyAdapter):
    __targetclass__ = 'javax.swing.JComboBox'
    __targetproperty__ = ('selectedItem', 'selectedIndex', 'selectedObjects')

    def addListeners(self, obj, callback, *args, **kwargs):
        from java.awt.event import ItemListener
        self.listener = addExplicitEventListener(obj, ItemListener,
            'itemStateChanged', callback, *args, **kwargs)


@registry.registerPropertyAdapter
class JSpinnerAdapter(DefaultPropertyAdapter):
    __targetclass__ = 'javax.swing.JSpinner'
    __targetproperty__ = ('value', 'nextValue', 'previousValue')

    def addListeners(self, obj, callback, *args, **kwargs):
        from javax.swing.event import ChangeListener
        self.listener = addExplicitEventListener(obj, ChangeListener,
            'stateChanged', callback, *args, **kwargs)
