"""
Provides a property adapter for JavaBeans binding and adapters for most
built-in Swing components.

"""
from __future__ import unicode_literals

from ...events import (addPropertyListener, addEventListener,
                       addRowSorterListener)
from . import BindingAdapter, registry


@registry.registerDefaultPropertyAdapter
class JavaBeansPropertyAdapter(BindingAdapter):
    """
    A default property adapter that uses JavaBeans binding
    (addPropertyListener, removePropertyListener) to listen to changes to the
    given property.

    """
    __slots__ = 'property'

    def __init__(self, options, property=None):
        BindingAdapter.__init__(self, options)
        self.property = property

    def addListeners(self, parent, callback, *args, **kwargs):
        self.listeners['property'] = addPropertyListener(
            parent, self.property, callback, *args, **kwargs)


@registry.registerPropertyAdapter
class ItemSelectableAdapter(JavaBeansPropertyAdapter):
    __slots__ = ()
    __targetclass__ = 'java.awt.ItemSelectable'
    __targetproperty__ = 'selected'

    def addListeners(self, parent, callback, *args, **kwargs):
        from java.awt.event import ItemListener
        self.listeners['item'] = addEventListener(
            parent, ItemListener, 'itemStateChanged', callback, *args,
            **kwargs)


@registry.registerPropertyAdapter
class JTextComponentAdapter(JavaBeansPropertyAdapter):
    """
    Adapter for text components like JTextField, JFormattedTextField and
    JTextArea.

    :ivar onFocusLost: ``True`` if the binding should be synchronized
        when the field loses focus, ``False`` to synchronize whenever the
        associated document is changed. Default is ``False``.

    """
    __slots__ = 'onFocusLost'
    __targetclass__ = 'javax.swing.text.JTextComponent'
    __targetproperty__ = 'text'

    def __init__(self, options, property):
        JavaBeansPropertyAdapter.__init__(self, options, property)
        self.onFocusLost = options.get('onFocusLost', False)

    def addListeners(self, parent, callback, *args, **kwargs):
        if self.onFocusLost:
            self.addFocusListener(parent, callback, *args, **kwargs)
        else:
            # Track changes to both JTextComponent.document and the
            # document itself
            self.addDocumentPropertyListener(parent, callback, *args, **kwargs)
            self.addDocumentListener(parent, callback, *args, **kwargs)

    def addFocusListener(self, parent, callback, *args, **kwargs):
        from java.awt.event import FocusListener
        self.listeners['focus'] = addEventListener(
            parent, FocusListener, 'focusLost', callback, *args, **kwargs)

    def addDocumentPropertyListener(self, parent, callback, *args, **kwargs):
        self.listeners['documentProperty'] = addPropertyListener(
            parent, 'document', self.documentPropertyChanged, parent, callback,
            *args, **kwargs)

    def addDocumentListener(self, parent, callback, *args, **kwargs):
        if parent.document is not None:
            from javax.swing.event import DocumentListener
            events = (u'changedUpdate', u'insertUpdate', u'removeUpdate')
            self.listeners['document'] = addEventListener(
                parent.document, DocumentListener, events, callback, *args,
                **kwargs)

    def documentPropertyChanged(self, event, parent, callback, *args,
                                **kwargs):
        self.removeListeners('document')
        callback(event, *args, **kwargs)
        self.addDocumentListener(parent, callback, *args, **kwargs)


@registry.registerPropertyAdapter
class JTreeAdapter(JavaBeansPropertyAdapter):
    __targetclass__ = 'javax.swing.JTree'
    __targetproperty__ = ('selectionCount', 'selectionPath', 'selectionPaths',
                          'selectionRows', 'lastSelectedPathComponent',
                          'leadSelectionRow', 'maxSelectionRow',
                          'minSelectionRow')

    def addListeners(self, parent, callback, *args, **kwargs):
        self.addSelectionModelListener(parent, callback, *args, **kwargs)
        self.addSelectionListener(parent, callback, *args, **kwargs)

    def addSelectionModelListener(self, parent, callback, *args, **kwargs):
        self.listeners['selectionModel'] = addPropertyListener(
            parent, 'selectionModel', self.selectionModelChanged, parent,
            callback, *args, **kwargs)

    def addSelectionListener(self, parent, callback, *args, **kwargs):
        selectionModel = parent.selectionModel
        if selectionModel is not None:
            from javax.swing.event import TreeSelectionListener
            self.listeners['selection'] = addEventListener(
                selectionModel, TreeSelectionListener, 'valueChanged',
                self.selectionChanged, callback, *args, **kwargs)

    def selectionModelChanged(self, event, parent, callback, *args, **kwargs):
        self.removeListeners('selection')
        self.selectionChanged(None, callback, *args, **kwargs)
        self.addSelectionListener(parent, callback, *args, **kwargs)

    def selectionChanged(self, event, callback, *args, **kwargs):
        if not event or not event.valueIsAdjusting or not self.ignoreAdjusting:
            callback(event, *args, **kwargs)


@registry.registerPropertyAdapter
class JListAdapter(JTreeAdapter):
    """
    Adapter for :class:`javax.swing.JList`.

    :ivar ignoreAdjusting: ``True`` if the callback should only be called
        when the selection list has finished adjusting.
        Default is ``True``.

    """
    __slots__ = 'ignoreAdjusting'
    __targetclass__ = 'javax.swing.JList'
    __targetproperty__ = ('selectedValue', 'selectedIndex', 'selectedIndices',
                          'leadSelectionIndex', 'anchorSelectionIndex',
                          'maxSelectionIndex', 'minSelectionIndex')

    def __init__(self, options, property):
        JavaBeansPropertyAdapter.__init__(self, options, property)
        self.ignoreAdjusting = options.get('ignoreAdjusting', True)

    def addSelectionListener(self, parent, callback, *args, **kwargs):
        selectionModel = parent.selectionModel
        if selectionModel is not None:
            from javax.swing.event import ListSelectionListener
            self.listeners['selection'] = addEventListener(
                selectionModel, ListSelectionListener, 'valueChanged',
                self.selectionChanged, callback, *args, **kwargs)


@registry.registerPropertyAdapter
class JTableRowSelectionAdapter(JListAdapter):
    """
    Adapter for row selection attributes on :class:`javax.swing.JTable`.

    :ivar ignoreAdjusting: ``True`` if the callback should only be called
        when the selection list has finished adjusting.
        Default is ``True``.

    """
    __slots__ = ()
    __targetclass__ = 'javax.swing.JTable'
    __targetproperty__ = ('selectedRow', 'selectedRows', 'selectedRowCount')


@registry.registerPropertyAdapter
class JTableColumnSelectionAdapter(JavaBeansPropertyAdapter):
    """
    Adapter for row selection attributes on :class:`javax.swing.JTable`.

    :ivar ignoreAdjusting: ``True`` if the callback should only be called
        when the selection list has finished adjusting.
        Default is ``True``.

    """
    __slots__ = 'ignoreAdjusting'
    __targetclass__ = 'javax.swing.JTable'
    __targetproperty__ = ('selectedColumn', 'selectedColumns',
                          'selectedColumnCount')

    def __init__(self, options, property):
        JavaBeansPropertyAdapter.__init__(self, options, property)
        self.ignoreAdjusting = options.get('ignoreAdjusting', True)

    def addListeners(self, parent, callback, *args, **kwargs):
        self.addColumnModelListener(parent, callback, *args, **kwargs)
        self.addSelectionListener(parent, callback, *args, **kwargs)

    def addColumnModelListener(self, parent, callback, *args, **kwargs):
        self.listeners['columnModel'] = addPropertyListener(
            parent, 'columnModel', self.columnModelChanged, parent, callback,
            *args, **kwargs)

    def addSelectionListener(self, parent, callback, *args, **kwargs):
        columnModel = parent.columnModel
        selectionModel = columnModel.selectionModel if columnModel else None
        if selectionModel is not None:
            from javax.swing.event import ListSelectionListener
            self.listeners['selection'] = addEventListener(
                selectionModel, ListSelectionListener, 'valueChanged',
                self.selectionChanged, callback, *args, **kwargs)

    def columnModelChanged(self, event, parent, callback, *args, **kwargs):
        self.removeListeners('selection')
        self.selectionChanged(None, callback, *args, **kwargs)
        self.addListeners(parent, callback, *args, **kwargs)

    def selectionChanged(self, event, callback, *args, **kwargs):
        if not event or not event.valueIsAdjusting or not self.ignoreAdjusting:
            callback(event, *args, **kwargs)


class RowSorterAdapter(JavaBeansPropertyAdapter):
    __slots__ = ()
    __targetclass__ = 'javax.swing.RowSorter'
    __targetproperty__ = 'viewRowCount'

    def addListeners(self, parent, callback, *args, **kwargs):
        self.listeners['rowsorter'] = addRowSorterListener(
            parent, callback, *args, **kwargs)


@registry.registerPropertyAdapter
class JComboBoxAdapter(JavaBeansPropertyAdapter):
    __slots__ = ()
    __targetclass__ = 'javax.swing.JComboBox'
    __targetproperty__ = ('selectedItem', 'selectedIndex', 'selectedObjects')

    def addListeners(self, parent, callback, *args, **kwargs):
        from java.awt.event import ItemListener
        self.listeners['itemState'] = addEventListener(
            parent, ItemListener, 'itemStateChanged', callback, *args,
            **kwargs)


@registry.registerPropertyAdapter
class JSpinnerAdapter(JComboBoxAdapter):
    __slots__ = ()
    __targetclass__ = 'javax.swing.JSpinner'
    __targetproperty__ = ('value', 'nextValue', 'previousValue')

    def addListeners(self, parent, callback, *args, **kwargs):
        from javax.swing.event import ChangeListener
        self.listeners['state'] = addEventListener(
            parent, ChangeListener, 'stateChanged', callback, *args, **kwargs)


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


@registry.registerListAdapter
@registry.registerPropertyAdapter
class ListModelAdapter(JavaBeansPropertyAdapter):
    __slots__ = ()
    __targetclass__ = 'javax.swing.ListModel'
    __targetproperty__ = 'size'

    def addListeners(self, parent, callback, *args, **kwargs):
        from javax.swing.event import ListDataListener
        events = ('contentsChanged', 'intervalAdded', 'intervalRemoved')
        self.listeners['list'] = addEventListener(
            parent, ListDataListener, events, callback, *args, **kwargs)


@registry.registerListAdapter
@registry.registerPropertyAdapter
class TableModelAdapter(JavaBeansPropertyAdapter):
    __slots__ = ()
    __targetclass__ = 'javax.swing.table.TableModel'
    __targetproperty__ = 'rowCount'

    def addListeners(self, parent, callback, *args, **kwargs):
        from javax.swing.event import TableModelListener
        self.listeners['table'] = addEventListener(
            parent, TableModelListener, 'tableChanged', callback, *args,
            **kwargs)
