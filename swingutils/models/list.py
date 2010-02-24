from javax.swing import AbstractListModel


class DelegateListModel(AbstractListModel):
    """
    A list model that delegates actual list operations to a plain list object,
    and fires the appropriate events on such operations.

    """
    def __init__(self, delegate=None):
        self._delegate = delegate

    def getDelegate(self):
        return self._delegate
    
    def setDelegate(self, value):
        oldLength = len(self._delegate) if self._delegate else 0
        self._delegate = value
        newLength = len(self._delegate) if self._delegate else 0

        minLength = min(oldLength, newLength)
        maxLength = max(oldLength, newLength)
        if maxLength:
            if maxLength > oldLength:
                self.fireIntervalAdded(self, minLength, maxLength - 1)
            elif maxLength < oldLength:
                self.fireIntervalRemoved(self, minLength, maxLength - 1)
            self.fireContentsChanged(self, 0, maxLength - 1)

    delegate = property(getDelegate, setDelegate)

    #
    # ListModel methods
    #

    def getSize(self):
        return len(self._delegate) if self._delegate else 0

    def getElementAt(self, index):
        return self._delegate[index]

    #
    # list methods
    #

    def __getitem__(self, index):
        return self._delegate.__getitem__(index)

    def __setitem__(self, index, value):
        oldLength = len(self._delegate)
        self._delegate.__setitem__(index, value)
        newLength = len(self._delegate)
        slice_ = index if isinstance(index, slice) else slice(index, index)
        start = slice_.start or 0
        end = slice_.stop or newLength

        if slice_.step:
            # Stepping can't remove or add items
            for i in xrange(start, end, slice_.step):
                self.fireContentsChanged(self, i, i)
        elif newLength > oldLength:
            # Items were added
            if start < oldLength:
                self.fireContentsChanged(self, start, oldLength - 1)
            self.fireIntervalAdded(self, oldLength, newLength - 1)
        elif newLength < oldLength:
            # Items were removed
            if newLength > 0:
                self.fireContentsChanged(self, start, newLength - 1)
            self.fireIntervalRemoved(self, newLength, oldLength - 1)
        else:
            # Items were changed
            self.fireContentsChanged(self, start, end)

    def __delitem__(self, index):
        self._delegate.__delitem__(index)
        slice_ = index if isinstance(index, slice) else slice(index, index)
        indices = slice_.indices(len(self._delegate))
        if indices[2] > 1:
            # Remove from bottom first so as not to cause problems
            range_ = xrange(indices[0], indices[1], indices[2])
            for i in reversed(range_):
                self.fireIntervalRemoved(self, i, i)
        else:
            self.fireIntervalRemoved(self, indices[0], indices[1])

    def __iter__(self):
        return self._delegate.__iter__()

    def __len__(self):
        return self._delegate.__len__() if self._delegate else 0

    def append(self, obj):
        self._delegate.append(obj)
        pos = len(self._delegate) - 1
        self.fireIntervalAdded(self, pos, pos)

    def insert(self, index, obj):
        self._delegate.insert(index, obj)
        self.fireIntervalAdded(self, index, index)

    def extend(self, items):
        start = len(self._delegate)
        self._delegate.extend(items)
        end = len(self._delegate)
        if end > start:
            self.fireIntervalAdded(self, start, end - 1)
