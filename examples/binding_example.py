# encoding: utf-8
import logging

from java.lang import String, Integer
from java.awt import GridLayout
from java.awt.event import ActionListener
from javax.swing import JLabel, JFrame, JFormattedTextField, JTextField, \
    JScrollPane, JTable, BoxLayout, JPanel, Box, BorderFactory, JButton
from javax.swing.ListSelectionModel import SINGLE_SELECTION

from swingutils.threads import asyncSwingTask
from swingutils.binding import BindingGroup, TWOWAY
from swingutils.models.table import ObjectTableModel, TableSelectionMirror
from swingutils.events import addEventListener
from swingutils.format import installNumberFormat


class Person(object):
    def __init__(self, firstName=None, lastName=None, birthYear=None):
        self.firstName = firstName
        self.lastName = lastName
        self.birthYear = birthYear


class MainFrame(JFrame):
    def __init__(self):
        JFrame.__init__(self, u'Jython-Swingutils Binding Demo')

        self.initComponents()
        self.initBinding()
        self.initEvents()
        self.initLayout()

        # Resize the window to accommodate the added components
        self.pack()

        # Center the window on the screen
        self.locationRelativeTo = None

        # Make the application quit when the window is closed
        self.defaultCloseOperation = JFrame.EXIT_ON_CLOSE

    def initComponents(self):
        peopleTableModel = ObjectTableModel([],
            (u'First name', String, 'firstName'),
            (u'Last name', String, 'lastName'),
            (u'Birth year', Integer, 'birthYear'))
        self.peopleTable = JTable(peopleTableModel,
                                  selectionMode=SINGLE_SELECTION)

        # Create a selection holder that tracks the row selection and
        # notifies the table model of any changes made to the object
        self.selection = TableSelectionMirror(self.peopleTable)

        self.firstNameField = JTextField()
        self.lastNameField = JTextField()
        self.birthYearField = JFormattedTextField()
        installNumberFormat(self.birthYearField, int, groupingUsed=False)
        self.summaryField = JTextField(15, editable=False)
        self.addButton = JButton(u'Add person')
        self.removeButton = JButton(u'Remove person')

    def initEvents(self):
        addEventListener(self.addButton, ActionListener, 'actionPerformed',
                         self.addPerson)
        addEventListener(self.removeButton, ActionListener, 'actionPerformed',
                         self.removePerson)

    def initBinding(self):
        group = BindingGroup()
        group.bind(self.peopleTable, 'model[selectedRow]',
                   self, 'selectedPerson')
        group.bind(self.selection, 'firstName', self.firstNameField, 'text',
                   mode=TWOWAY)
        group.bind(self.selection, 'lastName', self.lastNameField, 'text',
                   mode=TWOWAY)
        group.bind(self.selection, 'birthYear', self.birthYearField, 'value',
                   mode=TWOWAY)
        group.bind(self.selection,
            'u"%s %s, %s" % (firstName or u"?", lastName or u"?", '
            'birthYear or u"????")', self.summaryField, 'text')

        # Disable input fields and the remove button if nothing is selected
        for b in list(group.bindings):
            if b.mode == TWOWAY:
                field = b.targetExpression.root
                group.bind(self.peopleTable, 'selectedRow >= 0', field,
                           'enabled')

    def initLayout(self):
        # Create a horizontal layout and a 10 pixel border
        self.layout = BoxLayout(self.contentPane, BoxLayout.X_AXIS)
        self.contentPane.border = BorderFactory.createEmptyBorder(10, 10, 10,
                                                                  10)
        # Add the table
        self.add(JScrollPane(self.peopleTable))

        # Add a 10 pixel gap
        self.add(Box.createHorizontalStrut(10))

        # Create a vertical container
        vbox = Box(BoxLayout.Y_AXIS)
        self.add(vbox)

        # Add the form fields
        grid = JPanel(GridLayout(5, 2, 10, 10))
        grid.add(JLabel(u"First name"))
        grid.add(self.firstNameField)
        grid.add(JLabel(u"Last name"))
        grid.add(self.lastNameField)
        grid.add(JLabel(u"Birth year"))
        grid.add(self.birthYearField)
        grid.add(JLabel(u"Summary"))
        grid.add(self.summaryField)
        vbox.add(grid)

        # Add the buttons
        buttonRow = Box(BoxLayout.X_AXIS)
        buttonRow.add(self.addButton)
        buttonRow.add(Box.createHorizontalStrut(10))
        buttonRow.add(self.removeButton)
        vbox.add(buttonRow)

        vbox.add(Box.createVerticalGlue())

    def addPerson(self, event):
        person = Person()
        self.peopleTable.model.append(person)
        modelRow = self.peopleTable.model.getObjectIndex(person)
        viewRow = self.peopleTable.convertRowIndexToView(modelRow)
        self.peopleTable.addRowSelectionInterval(viewRow, viewRow)

        # Set the focus to the first name field
        self.firstNameField.grabFocus()

    def removePerson(self, event):
        viewRow = self.peopleTable.selectedRow
        modelRow = self.peopleTable.convertRowIndexToView(viewRow)
        del self.peopleTable.model[modelRow]


@asyncSwingTask
def createGUI():
    # All Swing operations should be executed in the Event Dispatch Thread
    MainFrame().visible = True


if __name__ == '__main__':
    # Just in case you want to see binding debug messages (make sure you
    # give the BindingGroup a Logger object in the "logger" keyword argument)
    logging.basicConfig(level=logging.DEBUG)

    createGUI()
