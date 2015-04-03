from java.lang import Object
from javax.swing.table import AbstractTableModel

from swingutils.models.list import AbstractDelegateList
from swingutils.beans import MirrorObject
from swingutils.events import addListSelectionListener, addPropertyListener


class DelegateTableModel(AbstractDelegateList, AbstractTableModel):
    """
    Table model that wraps any list-like object, and fires events when its
    contents are manipulated (through the table model).

    The :attr:`__columns__` attribute should be a sequence of
    (name, class) tuples. The `name` is used for displaying column headers, and
    `class` is used for identifying the type of objects in this column
    (usually for the purpose of choosing an appropriate cell renderer).
    You can either override :attr:`__columns__` in a subclass, or supply it via
    the constructor.

    List data is assumed to be a two-dimensional table (list of lists).

    """
    __columns__ = ()

    def __init__(self, delegate, *args):
        """
        Initializes the column names and types.
        You can supply the column names and types as a series of either
        (name, type) tuples or column names to the constructor, or provide a
        __columns__ variable in a subclass.

        :param delegate: the list where this table model gets its data from

        """
        super(DelegateTableModel, self).__init__(delegate)

        self.__columns__ = list(args if args else self.__columns__)
        for index, column in enumerate(self.__columns__):
            self.__columns__[index] = self._validateColumn(column, index)

    def _validateColumn(self, column, index):
        if isinstance(column, basestring):
            column = (column, Object)
        if not isinstance(column[0], basestring):
            raise ValueError('Column %d: name must be a string' % index)
        if not isinstance(column[1], type):
            raise ValueError('Column %d: type must be a type object' % index)
        return column

    def _fireItemsChanged(self, start, end):
        self.fireTableRowsUpdated(start, end)

    def _fireItemsAdded(self, start, end):
        self.fireTableRowsInserted(start, end)

    def _fireItemsRemoved(self, start, end):
        self.fireTableRowsDeleted(start, end)

    @property
    def delegate(self):
        return self._delegate

    @delegate.setter
    def delegate(self, value):
        self._delegate = value
        self.fireTableDataChanged()

    #
    # TableModel methods
    #

    def getColumnCount(self):
        return len(self.__columns__)

    def getRowCount(self):
        return len(self)

    def getValueAt(self, rowIndex, columnIndex):
        return self[rowIndex][columnIndex]

    #
    # Overridden AbstractTableModel methods
    #

    def getColumnClass(self, columnIndex):
        return self.__columns__[columnIndex][1]

    def getColumnName(self, columnIndex):
        return self.__columns__[columnIndex][0]

    def setValueAt(self, aValue, rowIndex, columnIndex):
        self[rowIndex][columnIndex] = aValue

    #
    # Convenience methods
    #

    def refresh(self):
        """
        Forces a visual refresh for all rows on related tables.
        Use this method to visually update tables after you have done changes
        that did not fire the appropriate table events.

        """
        if len(self) > 0:
            self.fireTableRowsUpdated(0, len(self) - 1)


class ObjectTableModel(DelegateTableModel):
    """
    A variant of :class:`DelegateTableModel` where each row in the delegate
    is assumed to be a single object.

    Columns are mapped to object attributes.
    The :attr:`__column__` attribute should be a sequence of
    (name, class, attrname) tuples where attrname is the name of the attribute
    the column is mapped to.

    """

    #
    # Overridden DelegateTableModel methods
    #

    def __init__(self, delegate, *args):
        # TODO: use super() when #1540 is fixed
        AbstractTableModel.__init__(self)
        AbstractDelegateList.__init__(self, delegate)

        self.__columns__ = list(args if args else self.__columns__)
        self._getters = [None] * len(self.__columns__)
        for index, column in enumerate(self.__columns__):
            self.__columns__[index] = self._validateColumn(column, index)

    def _validateColumn(self, column, index):
        column = DelegateTableModel._validateColumn(self, column, index)
        if len(column) < 3:
            raise ValueError('Column %d: missing object attribute name' %
                             index)
        if isinstance(column[2], basestring):
            self._getters[index] = lambda row: getattr(row, column[2])
        elif hasattr(column[2], '__call__'):
            self._getters[index] = column[2]
        else:
            raise ValueError('Column %d: object attribute name must either be '
                             'a string or a callable' % index)
        return column

    def getValueAt(self, rowIndex, columnIndex):
        line = self[rowIndex]
        return self._getters[columnIndex](line)

    def setValueAt(self, aValue, rowIndex, columnIndex):
        attrname = self.__columns__[columnIndex][2]
        setattr(self[rowIndex], attrname, aValue)
        self.fireTableCellUpdated(rowIndex, columnIndex)

    #
    # Convenience methods
    #

    def getObjectIndex(self, obj):
        """
        Returns the row number that contains the object that is equal
        to the given object.

        :return: the row number, or -1 if no match was found

        """
        for i, row in enumerate(self):
            if row == obj:
                return i
        return -1

    def getSelectedObject(self, table):
        """
        Returns the selected object, or first selected object if the table has
        multi-row selection enabled.

        """
        if table.selectedRow >= 0:
            modelRow = table.convertRowIndexToModel(table.selectedRow)
            return self[modelRow]

    def getSelectedObjects(self, table):
        """
        Returns objects that have been selected in the given table.
        This table model must be the given table's model.

        :return: objects that were selected in the given table
        :rtype: list

        """
        selected = []
        for viewRow in table.selectedRows:
            modelRow = table.convertRowIndexToModel(viewRow)
            selected.append(self[modelRow])
        return selected

    def getVisibleObjects(self, table):
        """
        Returns objects not hidden by any table filters.
        This table model must be the given table's model.

        :return: objects that were visible in the given table
        :rtype: list

        """
        visible = []
        for viewRow in xrange(table.rowCount):
            modelRow = table.convertRowIndexToModel(viewRow)
            visible.append(self[modelRow])
        return visible


class TableSelectionMirror(MirrorObject):
    """
    This class provides a "mirror" for the given table's currently selected
    object, with support for bound properties regardless of whether the
    target object itself supports bound properties or not.

    This is only useful for use with list-like table models, such as
    :class:`~ObjectTableModel`.

    """
    __slots__ = ('_table', '_selectionListener')

    def __init__(self, table):
        if not hasattr(table.model, '__getitem__'):
            raise TypeError('Table model must support indexed access')
        self._table = table
        self._selectionListener = addListSelectionListener(
            table.selectionModel, self._tableSelectionChanged)
        addPropertyListener(self, None, self._propertyChanged)

    def _propertyChanged(self, event):
        """Invoked on a property change event in this object."""

        self._table.repaint()

    def _tableSelectionChanged(self, event):
        """Invoked on a table selection change."""

        if not event.valueIsAdjusting:
            selectedRows = self._table.selectedRows
            selectedRow = selectedRows[0] if len(selectedRows) == 1 else -1

            if selectedRow >= 0:
                modelRow = self._table.convertRowIndexToModel(selectedRow)
                self._delegate = self._table.model[modelRow]
            else:
                self._delegate = None

    def _detach(self):
        """Remove all event listeners."""

        if self._selectionListener:
            self._selectionListener.unlisten()
            self._selectionListener = None
