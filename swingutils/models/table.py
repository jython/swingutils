from java.lang import Object
from javax.swing.table import AbstractTableModel

from swingutils.models.list import AbstractDelegateList


class DelegateTableModel(AbstractTableModel, AbstractDelegateList):
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

        """
        if args:
            self.__columns__ = args

        for index, column in enumerate(self.__columns__):
            self._validateColumn(column, index)

    def _validateColumn(self, column, index):
        if isinstance(column, basestring):
            self.__columns__[index] = (column, Object)
        if not isinstance(column[0], basestring):
            raise ValueError('Column %d: name must be a string' % index)
        if not isinstance(column[1], type):
            raise ValueError('Column %d: type must be a type object' % index)

    def _fireItemsChanged(self, start, end):
        self.fireTableRowsUpdated(self, start, end)

    def _fireItemsAdded(self, start, end):
        self.fireTableRowsInserted(self, start, end)

    def _fireItemsRemoved(self, start, end):
        self.fireTableRowsDeleted(self, start, end)

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

    def getSelectedRow(self, table):
        """
        Returns the selected row, or first selected row if the table has
        multi-row selection enabled.

        """
        assert table.model is self
        if table.selectedRow >= 0:
            modelRow = table.convertRowIndexToModel(table.selectedRow)
            return self[modelRow]

    def getSelectedRows(self, table):
        """
        Returns rows that have been selected in the given table.
        This table model must be the given table's model.

        :return: rows that were selected in the given table
        :rtype: list

        """
        assert table.model is self
        selected = []
        for viewRow in table.selectedRows:
            modelRow = table.convertRowIndexToModel(viewRow)
            selected.append(self[modelRow])
        return selected

    def getVisibleRows(self, table):
        """
        Returns rows not hidden by any table filters.
        This table model must be the given table's model.

        :return: rows that were visible in the given table
        :rtype: list

        """
        assert table.model is self
        visible = []
        for viewRow in xrange(table.rowCount):
            modelRow = table.convertRowIndexToModel(viewRow)
            visible.append(self[modelRow])
        return visible

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

    def _validateColumn(self, column, index):
        DelegateTableModel._validateColumn(column)
        if len(column) < 3:
            raise ValueError('Column %d: missing object attribute name' %
                             index)
        if not isinstance(column[2], basestring):
            raise ValueError('Column %d: object attribute name must be a '
                             'string' % index)

    def getValueAt(self, rowIndex, columnIndex):
        attrname = self.__columns__[columnIndex][2]
        return getattr(self[rowIndex], attrname)

    def setValueAt(self, aValue, rowIndex, columnIndex):
        attrname = self.__columns__[columnIndex][2]
        setattr(self[rowIndex], attrname, aValue)
        self.fireTableCellUpdated(rowIndex, columnIndex)

    #
    # Convenience methods
    #

    def getRowIndex(self, obj):
        """
        Returns the row number that contains the object that is equal
        to the given object.

        :return: the row number, or -1 if no match was found

        """
        for i, row in enumerate(self):
            if row == obj:
                return i
        return -1
