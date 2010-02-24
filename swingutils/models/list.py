from javax.swing import AbstractListModel


class AbstractDelegateList(object):
    """
    An abstract class that acts as a proxy to an actual list object.
    Supports firing events for additions/removals/changes, but these methods
    must be implemented in a subclass.
    
    """
    def __init__(self, delegate):
        self._delegate = delegate

    #
    # Getter and setter for the "delegate" property
    #

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
                self._fireItemsAdded(minLength, maxLength - 1)
            elif maxLength < oldLength:
                self._fireItemsRemoved(minLength, maxLength - 1)
            self._fireItemsChanged(0, maxLength - 1)

    delegate = property(getDelegate, setDelegate)
    
    #
    # 
    #

    def _fireItemsChanged(self, start, end):
        raise NotImplementedError

    def _fireItemsAdded(self, start, end):
        raise NotImplementedError

    def _fireItemsRemoved(self, start, end):
        raise NotImplementedError

    #
    # Methods to emulate the "list" type
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
                self._fireItemsChanged(i, i)
        elif newLength > oldLength:
            # Items were added
            if start < oldLength:
                self._fireItemsChanged(start, oldLength - 1)
            self._fireItemsAdded(oldLength, newLength - 1)
        elif newLength < oldLength:
            # Items were removed
            if newLength > 0:
                self._fireItemsChanged(start, newLength - 1)
            self._fireItemsRemoved(newLength, oldLength - 1)
        else:
            # Items were changed
            self._fireItemsChanged(start, end)

    def __delitem__(self, index):
        self._delegate.__delitem__(index)
        slice_ = index if isinstance(index, slice) else slice(index, index)
        indices = slice_.indices(len(self._delegate))
        if indices[2] > 1:
            # Remove from bottom first so as not to cause problems with indices
            range_ = xrange(indices[0], indices[1], indices[2])
            for i in reversed(range_):
                self._fireItemsRemoved(i, i)
        else:
            self._fireItemsRemoved(indices[0], indices[1])

    def __iter__(self):
        return self._delegate.__iter__()

    def __len__(self):
        return self._delegate.__len__() if self._delegate else 0

    def append(self, obj):
        self._delegate.append(obj)
        pos = len(self._delegate) - 1
        self._fireItemsAdded(pos, pos)

    def insert(self, index, obj):
        self._delegate.insert(index, obj)
        self._fireItemsAdded(index, index)

    def extend(self, items):
        start = len(self._delegate)
        self._delegate.extend(items)
        end = len(self._delegate)
        if end > start:
            self._fireItemsAdded(start, end - 1)


class DelegateListModel(AbstractListModel, AbstractDelegateList):
    """A delegate list model that provides a ListModel interface."""

    def __init__(self, delegate=None):
        AbstractListModel.__init__(self)
        AbstractDelegateList.__init__(self, delegate)

    def _fireItemsChanged(self, start, end):
        self.fireContentsChanged(self, start, end)

    def _fireItemsAdded(self, start, end):
        self.fireIntervalAdded(self, start, end)

    def _fireItemsRemoved(self, start, end):
        self.fireIntervalRemoved(self, start, end)

    #
    # ListModel methods
    #

    def getSize(self):
        return len(self)

    def getElementAt(self, index):
        return self[index]
