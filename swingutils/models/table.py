from java.lang import Object
from javax.swing.table import AbstractTableModel
from types import NoneType


class ListTableModel(AbstractTableModel, list):
    """Table model that wraps a Python `list` object, and fires events when its
    contents are manipulated (through the table model).

    """

    def __init__(self, *columns):
        """
        :param columns: a list of of column names or tuples of
                        (column name, column class)

        """
        self.columns = []

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

    #
    # Overridden methods from list
    #

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
        """TODO: should probably fire an interval changed event too"""
        list.__setslice__(self, start, end, value)
        self.fireTableRowsUpdated(start, end - 1)

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

    # Inherited methods from AbstractTableModel

    def getColumnClass(self, columnIndex):
        col = self.columns[columnIndex]
        if isinstance(col, tuple):
            return col[1]
        if len(self):
            type_ = type(self[0][columnIndex])
            if type_ is not NoneType:
                return type_
        return Object

    def getColumnCount(self):
        return len(self.columns)

    def getColumnName(self, columnIndex):
        col = self.columns[columnIndex]
        if isinstance(col, tuple):
            return col[0]
        return col

    def getRowCount(self):
        return len(self)

    def getValueAt(self, rowIndex, columnIndex):
        return self[rowIndex][columnIndex]

    def setValueAt(self, aValue, rowIndex, columnIndex):
        self[rowIndex][columnIndex] = aValue
        self.fireTableCellUpdated(rowIndex, columnIndex)
