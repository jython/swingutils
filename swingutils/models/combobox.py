from javax.swing import MutableComboBoxModel

from swingutils.models.list import ListModel


class ListComboModel(ListModel, MutableComboBoxModel):
    """
    Combo box model that is also a Python `list` object, and fires events
    when its contents are manipulated.

    """
    _selectedItem = None
    
    def __init__(self, *args):
        ListModel.__init__(self, *args)

    # ComboBoxModel methods

    def getSelectedItem(self):
        return self._selectedItem

    def setSelectedItem(self, anItem):
        if self._selectedItem != anItem:
            self._selectedItem = anItem
            self.fireContentsChanged(self, -1, -1)

    # MutableComboBoxModel methods

    def addElement(self, obj):
        self.append(obj)

    def insertElementAt(self, obj, index):
        self.insert(index, obj)

    def removeElement(self, obj):
        self.remove(obj)

    def removeElementAt(self, index):
        del self[index]
