from javax.swing import AbstractListModel


class ListModel(AbstractListModel, list):
    """List model that is also a Python `list` object, and fires events when
    its contents are manipulated.

    """    
    def __init__(self, *args):
        list.__init__(self, *args)

    #
    # list methods
    #

    def __delitem__(self, index):
        list.__delitem__(self, index)
        self.fireIntervalRemoved(self, index, index)

    def __delslice__(self, start, end):
        list.__delslice__(self, start, end)
        self.fireIntervalRemoved(self, start, end - 1)
    
    def __setitem__(self, index, value):
        list.__setitem__(self, index, value)
        self.fireContentsChanged(self, index, index)

    def __setslice__(self, start, end, value):
        # This can change, add and remove rows
        oldLength = len(self)
        list.__setslice__(self, start, end, value)
        newLength = len(self)

        if newLength > 0 and oldLength > 0:
            self.fireContentsChanged(self, start, min(oldLength,
                                                      newLength) - 1)
        if newLength > oldLength:
            self.fireIntervalAdded(self, oldLength, newLength - 1)
        elif newLength < oldLength:
            self.fireIntervalRemoved(self, newLength, oldLength - 1)

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
