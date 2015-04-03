from javax.swing import AbstractListModel

from swingutils.beans import MirrorObject
from swingutils.events import addPropertyListener, addListSelectionListener


class AbstractDelegateList(object):
    """
    An abstract class that acts as a proxy to an actual list object.
    Supports firing events for additions/removals/changes, but these methods
    must be implemented in a subclass.

    """
    def __init__(self, delegate=None):
        # TODO: add this back when Jython bug #1540 has been fixed
        # super(AbstractDelegateList, self).__init__()
        self._delegate = delegate

    #
    # Getter and setter for the "delegate" property
    #

    @property
    def delegate(self):
        return self._delegate

    @delegate.setter
    def delegate(self, value):
        oldLength = len(self._delegate) if self._delegate else 0
        self._delegate = value
        newLength = len(self._delegate) if self._delegate else 0

        minLength = min(oldLength, newLength)
        maxLength = max(oldLength, newLength)

        if newLength > oldLength:
            self._fireItemsAdded(minLength, maxLength - 1)
        elif newLength < oldLength:
            self._fireItemsRemoved(minLength, maxLength - 1)
        if minLength > 0:
            self._fireItemsChanged(0, minLength - 1)

    #
    # Abstract methods to fire event changes
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
        start = slice_.start if slice_.start is not None else 0
        end = slice_.stop if slice_.stop is not None else newLength

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
        if self._delegate is None:
            return tuple().__iter__()
        return self._delegate.__iter__()

    def __len__(self):
        if self._delegate is None:
            return 0
        return self._delegate.__len__()

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

    def count(self, obj):
        if self._delegate is None:
            return 0
        return self._delegate.count(obj)

    def index(self, obj, *args):
        if self._delegate is None:
            raise ValueError('x not in list')
        return self._delegate.index(obj, *args)

    def remove(self, obj):
        del self[self.index(obj)]


class DelegateListModel(AbstractDelegateList, AbstractListModel):
    """
    A delegate list model that provides a :class:`~javax.swing.ListModel`
    interface.
    """

    def __init__(self, delegate=None):
        super(DelegateListModel, self).__init__(delegate)

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


class ListSelectionMirror(MirrorObject):
    """
    This class provides a "mirror" for the given list component's currently
    selected object, with support for bound properties regardless of whether
    the target object itself supports bound properties or not.

    """
    __slots__ = ('_list', '_selectionListener')

    def __init__(self, list_):
        super(ListSelectionMirror, self).__init__()
        self._list = list_
        self._selectionListener = addListSelectionListener(
            list.selectionModel, self._selectionChanged)
        addPropertyListener(self, None, self._propertyChanged)

    def _propertyChanged(self, event):
        """Invoked on a property change event in this object."""

        self._list.repaint()

    def _selectionChanged(self, event):
        """Invoked on a list selection change."""

        if not event.valueIsAdjusting:
            self._delegate = self._list.selectedValue

    def _detach(self):
        """Remove all event listeners."""

        if self._selectionListener:
            self._selectionListener.unlisten()
            self._selectionListener = None
