from swingutils.events import addPropertyListener, addEventListener


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
        classNames = cls.__targetclass__
        if isinstance(cls.__targetclass__, basestring):
            classNames = (cls.__targetclass__,)

        properties = cls.__targetproperty__
        if isinstance(cls.__targetproperty__, basestring):
            properties = (cls.__targetproperty__,)

        for className in classNames:
            for property in properties:
                key = (className, property)
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
        adapterClass = DefaultListAdapter
        for className in targetClassNames:
            if className in self.listAdapters:
                adapterClass = self.listAdapters[className]
                break

        return adapterClass(options)

    def dumpAdapters(self):
        """Prints a list of all registered adapters to standard output."""
        
        print 'Registered property adapters:'
        for key in sorted(self.propertyAdapters.keys()):
            adapter = self.propertyAdapters[key]
            print '* %s (class=%s property=%s)' % (adapter.__name__, key[0],
                                                   key[1])

        print
        print 'Registered list adapters:'
        for key in sorted(self.listAdapters.keys()):
            adapter = self.listAdapters[key]
            print '* %s (class=%s)' % (adapter, key)

registry = AdapterRegistry()


class BindingAdapter(object):
    __slots__ = ('listeners')

    def __init__(self, options, size=1):
        self.listeners = [None] * size

    def addListeners(self, parent, callback, args, kwargs):
        pass

    def removeListeners(self, index=0):
        for i in xrange(index, len(self.listeners)):
            if self.listeners[i] is not None:
                self.listeners[i].unlisten()
                self.listeners[i] = None

    def getValue(self, parent):
        raise NotImplementedError

    def setValue(self, parent, value):
        raise NotImplementedError


class DefaultPropertyAdapter(BindingAdapter):
    __slots__ = ('property')

    def __init__(self, property, options, size=1):
        BindingAdapter.__init__(self, options, size)
        self.property = property

    def addListeners(self, parent, callback, args, kwargs):
        self.listeners[0] = addPropertyListener(parent, self.property,
                                                callback, *args, **kwargs)

    def getValue(self, parent):
        return getattr(parent, self.property, None)

    def setValue(self, parent, value):
        setattr(parent, self.property, value)


class DefaultListAdapter(BindingAdapter):
    __slots__ = ()

    def getValue(self, parent, index):
        return parent[index]

    def setValue(self, parent, index, value):
        parent[index] = value


@registry.registerPropertyAdapter
class ItemSelectableAdapter(DefaultPropertyAdapter):
    __slots__ = ()
    __targetclass__ = 'java.awt.ItemSelectable'
    __targetproperty__ = 'selected'

    def addListeners(self, parent, callback, args, kwargs):
        from java.awt.event import ItemListener
        self.listeners[0] = addEventListener(parent, ItemListener,
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
    __slots__ = ('onFocusLost')
    __targetclass__ = 'javax.swing.text.JTextComponent'
    __targetproperty__ = 'text'

    def __init__(self, property, options):
        self.onFocusLost = options.get('onFocusLost', False)
        size = 1 if self.onFocusLost else 2
        DefaultPropertyAdapter.__init__(self, options, property, size)

    def addListeners(self, parent, callback, args, kwargs, index=0):
        if self.onFocusLost:
            from java.awt.event import FocusListener
            self.listeners[0] = addEventListener(parent, FocusListener,
                'focusLost', callback, *args, **kwargs)
        else:
            # Track changes to both JTextComponent.document and the
            # document itself
            if index <= 0:
                self.listeners[0] = addPropertyListener(parent, 'document',
                    self.documentChanged, parent, callback, *args, **kwargs)

            document = parent.document
            if index <= 1 and document is not None:
                from javax.swing.event import DocumentListener
                events = (u'changedUpdate', u'insertUpdate', u'removeUpdate')
                self.listeners[1] = addEventListener(document,
                    DocumentListener, events, callback, *args, **kwargs)

    def documentChanged(self, event, parent, callback, args, kwargs):
        self.removeListeners(1)
        callback(*args, **kwargs)
        self.addListeners(parent, callback, args, kwargs, 1)


@registry.registerPropertyAdapter
class JListAdapter(DefaultPropertyAdapter):
    """
    Adapter for :class:`javax.swing.JList`.

    :ivar ignoreAdjusting: ``True`` if the callback should only be called
        when the selection list has finished adjusting.
        Default is ``True``.

    """
    __slots__ = ('ignoreAdjusting')
    __targetclass__ = 'javax.swing.JList'
    __targetproperty__ = ('selectedValue', 'selectedIndex', 'selectedIndices',
                          'leadSelectionIndex', 'anchorSelectionIndex',
                          'maxSelectionIndex', 'minSelectionIndex')

    def __init__(self, property, options):
        DefaultPropertyAdapter.__init__(self, property, options, 2)
        self.ignoreAdjusting = options.get('ignoreAdjusting', True)

    def addListeners(self, parent, callback, args, kwargs, index=0):
        if index <= 0:
            self.listeners[0] = addPropertyListener(parent, 'selectionModel',
                self.selectionModelChanged, parent, callback, args, kwargs)

        selectionModel = parent.selectionModel
        if index <= 1 and selectionModel is not None:
            from javax.swing.event import ListSelectionListener
            self.listeners[1] = addEventListener(selectionModel,
                ListSelectionListener, 'valueChanged', self.selectionChanged,
                callback, args, kwargs)

    def selectionModelChanged(self, event, parent, callback, args, kwargs):
        self.removeListeners(1)
        self.selectionChanged(None, callback, args, kwargs)
        self.addListeners(parent, callback, args, kwargs, 1)

    def selectionChanged(self, event, callback, args, kwargs):
        if not event.valueIsAdjusting or not self.ignoreAdjusting:
            callback(event, *args, **kwargs)


@registry.registerPropertyAdapter
class JTableRowSelectionAdapter(DefaultPropertyAdapter):
    """
    Adapter for row selection attributes on :class:`javax.swing.JTable`.

    :ivar ignoreAdjusting: ``True`` if the callback should only be called
        when the selection list has finished adjusting.
        Default is ``True``.

    """
    __slots__ = ('ignoreAdjusting')
    __targetclass__ = 'javax.swing.JTable'
    __targetproperty__ = ('selectedRow', 'selectedRows', 'selectedRowCount')

    def __init__(self, property, options):
        DefaultPropertyAdapter.__init__(self, property, options, 2)
        self.ignoreAdjusting = options.get('ignoreAdjusting', True)

    def addListeners(self, parent, callback, args, kwargs, index=0):
        self.listeners[0] = addPropertyListener(parent, 'selectionModel',
            self.selectionModelChanged, parent, callback, args, kwargs)

        selectionModel = parent.selectionModel
        if index <= 1 and selectionModel is not None:
            from javax.swing.event import ListSelectionListener
            self.listeners[1] = addEventListener(
                selectionModel, ListSelectionListener, 'valueChanged',
                self.selectionChanged, callback, args, kwargs)

    def selectionModelChanged(self, event, parent, callback, args, kwargs):
        self.removeListeners(1)
        self.selectionChanged(None, callback, args, kwargs)
        self.addListeners(parent, callback, args, kwargs, 1)

    def selectionChanged(self, event, callback, args, kwargs):
        if not event or not event.valueIsAdjusting or not self.ignoreAdjusting:
            callback(event, *args, **kwargs)


@registry.registerPropertyAdapter
class JTableColumnSelectionAdapter(DefaultPropertyAdapter):
    """
    Adapter for row selection attributes on :class:`javax.swing.JTable`.

    :ivar ignoreAdjusting: ``True`` if the callback should only be called
        when the selection list has finished adjusting.
        Default is ``True``.

    """
    __slots__ = ('ignoreAdjusting')
    __targetclass__ = 'javax.swing.JTable'
    __targetproperty__ = ('selectedColumn', 'selectedColumns',
                          'selectedColumnCount')

    def __init__(self, property, options):
        DefaultPropertyAdapter.__init__(self, property, options, 2)
        self.ignoreAdjusting = options.get('ignoreAdjusting', True)

    def addListeners(self, parent, callback, args, kwargs, index=0):
        if index <= 0:
            self.listeners[0] = addPropertyListener(parent, 'columnModel',
                self.columnModelChanged, parent, callback, args, kwargs)

        columnModel = parent.columnModel
        selectionModel = columnModel.selectionModel if columnModel else None
        if index <= 1 and selectionModel is not None:
            from javax.swing.event import ListSelectionListener
            self.listeners[1] = addEventListener(
                columnModel.selectionModel, ListSelectionListener,
                'valueChanged', self.selectionChanged, callback, args, kwargs)

    def columnModelChanged(self, event, parent, callback, args, kwargs):
        self.removeListeners(1)
        self.selectionChanged(None, callback, args, kwargs)
        self.addListeners(parent, callback, args, kwargs)

    def selectionChanged(self, event, callback, args, kwargs):
        if not event or not event.valueIsAdjusting or not self.ignoreAdjusting:
            callback(event, *args, **kwargs)


@registry.registerPropertyAdapter
class JComboBoxAdapter(DefaultPropertyAdapter):
    __slots__ = ()
    __targetclass__ = 'javax.swing.JComboBox'
    __targetproperty__ = ('selectedItem', 'selectedIndex', 'selectedObjects')

    def addListeners(self, parent, callback, args, kwargs):
        from java.awt.event import ItemListener
        self.listeners[0] = addEventListener(parent, ItemListener,
            'itemStateChanged', callback, *args, **kwargs)


@registry.registerPropertyAdapter
class JSpinnerAdapter(JComboBoxAdapter):
    __slots__ = ()
    __targetclass__ = 'javax.swing.JSpinner'
    __targetproperty__ = ('value', 'nextValue', 'previousValue')

    def addListeners(self, parent, callback, args, kwargs):
        from javax.swing.event import ChangeListener
        self.listeners[0] = addEventListener(parent, ChangeListener,
            'stateChanged', callback, *args, **kwargs)


@registry.registerPropertyAdapter
class JSliderAdapter(JSpinnerAdapter):
    __slots__ = ()
    __targetclass__ = 'javax.swing.JSlider'
    __targetproperty__ = 'value'


@registry.registerPropertyAdapter
class JProgressBarAdapter(JSpinnerAdapter):
    __slots__ = ()
    __targetclass__ = 'javax.swing.JProgressBar'
    __targetproperty__ = ('value', 'percentComplete')
