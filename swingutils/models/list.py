from javax.swing import AbstractListModel


class ListModel(AbstractListModel, list):
    """List model that is also a Python `list` object, and fires events when
    its contents are manipulated (through the list model).

    """

    def replace(self, replacement):
        """Replaces the data with the given replacement.

        :type replacement: list or any iterable

        """
        if not isinstance(replacement, list):
            if not hasattr(replacement, '__iter__'):
                raise TypeError('replacement must be iterable')
            replacement = list(replacement)
        oldLength = len(self)
        if oldLength:
            list.__delslice__(self, 0, oldLength)
            self.fireIntervalRemoved(0, oldLength - 1)

        list.extend(self, replacement)
        if len(self):
            self.fireIntervalAdded(0, len(self) - 1)

    #
    # Overridden methods from list
    #

    def __delitem__(self, index):
        list.__delitem__(self, index)
        self.fireIntervalRemoved(self, index, index)

    def __delslice__(self, start, end):
        list.__delslice__(self, start, end)
        self.fireIntervalRemoved(self, start, end - 1)
    
    def __setitem__(self, index, value):
        list.__setitem__(self, index, value)
        self.fireContentsChanged(index, index)

    def __setslice__(self, start, end, value):
        """TODO: should probably fire an interval changed event too"""
        list.__setslice__(self, start, end, value)
        self.fireContentsChanged(start, end - 1)

    def append(self, obj):
        list.append(self, obj)
        length = len(self)
        self.fireIntervalAdded(self, length - 1, length - 1)

    def insert(self, index, obj):
        list.insert(self, index, obj)
        self.fireIntervalAdded(self, index, index)

    def extend(self, items):
        start = len(self)
        list.extend(self, items)
        end = len(self)
        if end > start:
            self.fireIntervalAdded(self, start, end - 1)

    #
    # ListModel methods
    #

    def getSize(self):
        return len(self)

    def getElementAt(self, index):
        return self[index]
