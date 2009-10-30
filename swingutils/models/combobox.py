from javax.swing import MutableComboBoxModel

from swingutils.models.list import ListModel


class ListComboModel(ListModel, MutableComboBoxModel):
    """Combo box model that is also a Python `list` object, and fires events
    when its contents are manipulated.

    """
    _selectedItem = None

    # ComboBoxModel methods

    def getSelectedItem(self):
        return self._selectedItem

    def setSelectedItem(self, anItem):
        self._selectedItem = anItem

    # MutableComboBoxModel methods

    def addElement(self, obj):
        self.append(obj)

    def insertElementAt(self, obj, index):
        self.insert(index, obj)

    def removeElement(self, obj):
        self.remove(obj)

    def removeElementAt(self, index):
        del self[index]
