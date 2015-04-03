from javax.swing import MutableComboBoxModel

from swingutils.models.list import DelegateListModel


class DelegateComboBoxModel(DelegateListModel, MutableComboBoxModel):
    """
    A Combo box model that wraps a list-like object, and fires events
    when its contents are manipulated.

    """
    _selectedItem = None

    def __init__(self, delegate=None):
        # TODO: use super() when #1540 is fixed
        DelegateListModel.__init__(self, delegate)

    #
    # ComboBoxModel methods
    #

    def getSelectedItem(self):
        return self._selectedItem

    def setSelectedItem(self, anItem):
        if self._selectedItem != anItem:
            self._selectedItem = anItem
            self.fireContentsChanged(self, -1, -1)

    #
    # MutableComboBoxModel methods
    #

    def addElement(self, obj):
        self.append(obj)

    def insertElementAt(self, obj, index):
        self.insert(index, obj)

    def removeElement(self, obj):
        self.remove(obj)

    def removeElementAt(self, index):
        del self[index]
