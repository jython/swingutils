from java.lang import Object
from javax.swing.table import AbstractTableModel


class ListTableModel(AbstractTableModel, list):
    """
    Table model that wraps a Python `list` object, and fires events when its
    contents are manipulated (through the table model).

    The :attr:`__columns__` attribute should be a sequence of
    (name, class) tuples. The `name` is used for displaying column headers, and
    `class` is used for identifying the type of objects in this column
    (usually for the purpose of choosing an appropriate cell renderer).
    You can either override :attr:`__columns__` in a subclass, or supply it via
    the constructor.

    """
    __columns__ = ()

    def __init__(self, *columns):
        """
        Initializes the column names and types.
        Constructor arguments override any column definitions from the class.
        
        :param columns: tuples of (column name, column class)

        """
        columns = columns or self.__columns__
        self.__columns__ = tuple(self._validateColumn(col) for col in columns)

    @staticmethod
    def _validateColumn(column):
        if isinstance(column, basestring):
            return (column, Object)
        if not isinstance(column[1], type):
            raise ValueError('Column "%s": expected a type for second item, '
                             'got %s instead' % (column[0], type(column[1])))
        return column

    def replace(self, replacement):
        """Replaces the data with the given replacement.

        :type replacement: list or any iterable

        """
        if not isinstance(replacement, list):
            if not hasattr(replacement, '__iter__'):
                raise TypeError('replacement must be iterable')
            replacement = list(replacement)
        list.__delslice__(self, 0, len(self))
        list.extend(self, replacement)
        self.fireTableDataChanged()

    # Methods from list

    def __delitem__(self, index):
        list.__delitem_(self, index)
        self.fireTableRowsDeleted(index, index)

    def __delslice__(self, start, end):
        list.__delslice__(self, start, end)
        self.fireTableRowsDeleted(start, end - 1)

    def __setitem__(self, row, value):
        list.__setitem__(self, row, value)
        self.fireTableRowsUpdated(row, row)

    def __setslice__(self, start, end, value):
        oldEnd = len(self) - 1
        list.__setslice__(self, start, end, value)
        self.fireTableRowsUpdated(start, min(oldEnd, end - 1))
        if end > oldEnd:
            self.fireTableRowsInserted(oldEnd + 1, end)

    def append(self, obj):
        list.append(self, obj)
        length = len(self)
        self.fireTableRowsInserted(length - 1, length - 1)

    def insert(self, index, obj):
        list.insert(self, index, obj)
        self.fireTableRowsInserted(index, index)

    def extend(self, items):
        start = len(self)
        list.extend(self, items)
        end = len(self)
        if end > start:
            self.fireTableRowsInserted(start, end - 1)

    # Methods from AbstractTableModel

    def getColumnClass(self, columnIndex):
        return self.__columns__[columnIndex][1] or Object

    def getColumnCount(self):
        return len(self.__columns__)

    def getColumnName(self, columnIndex):
        return self.__columns__[columnIndex][0]

    def getRowCount(self):
        return len(self)

    def getValueAt(self, rowIndex, columnIndex):
        return self[rowIndex][columnIndex]

    def setValueAt(self, aValue, rowIndex, columnIndex):
        self[rowIndex][columnIndex] = aValue
        self.fireTableCellUpdated(rowIndex, columnIndex)

    # Convenience methods

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
        for viewRow in xrange(0, table.rowCount):
            modelRow = table.convertRowIndexToModel(viewRow)
            visible.append(self[modelRow])
        return visible

    def refresh(self):
        """
        Forces a visual refresh for all rows on related tables.
        Use this method to visually update tables after you have done changes
        that did not fire the appropriate table events.

        """
        if len(self.data) > 0:
            self.fireTableRowsUpdated(0, len(self.data) - 1)


class ObjectTableModel(ListTableModel):
    """
    A variant of :class:`ListTableModel` where each row is a single object.
    Columns are mapped to object attributes.
    The :attr:`__column__` attribute should be a sequence of
    (name, class, attrname) tuples where attrname is the name of the attribute
    the column is mapped to.

    """
    @staticmethod
    def _validateColumn(column):
        column = ListTableModel._validateColumn(column)
        if not isinstance(column[2], basestring):
            raise ValueError('Column "%s": the attribute name must be a '
                             'string' % column[0])
        return column

    # Methods from AbstractTableModel

    def getValueAt(self, rowIndex, columnIndex):
        attrname = self.__columns__[columnIndex][2]
        return getattr(self[rowIndex], attrname)

    def setValueAt(self, aValue, rowIndex, columnIndex):
        attrname = self.__columns__[columnIndex][2]
        setattr(self[rowIndex], attrname, aValue)
        self.fireTableCellUpdated(rowIndex, columnIndex)

    # Convenience methods

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
