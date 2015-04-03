from array import array
import logging

from java.lang import String, Integer
from javax.swing import JTextField, JFormattedTextField, JList, JComboBox, \
    SpinnerNumberModel, JSpinner, JSlider, JProgressBar, JTable, \
    DefaultListSelectionModel, JCheckBox
from javax.swing.table import DefaultTableColumnModel, TableColumn

from nose.tools import eq_

from swingutils.binding import BindingGroup, BindingExpression, TWOWAY, MANUAL
from swingutils.beans import AutoChangeNotifier, JavaBeanSupport
from swingutils.models.list import DelegateListModel
from swingutils.models.combobox import DelegateComboBoxModel
from swingutils.models.table import ObjectTableModel


class Person(JavaBeanSupport, AutoChangeNotifier):
    def __init__(self, firstName=None, lastName=None, birthYear=None):
        self.firstName = firstName
        self.lastName = lastName
        self.birthYear = birthYear
        self.children = []

    def getChild(self, index):
        return self.children[index]


class DummyObject(JavaBeanSupport, AutoChangeNotifier):
    value = None


class TestExpressions(object):
    def setup(self):
        self.person = Person(u'Joe', u'Average', 1970)

    def testReadSimpleProperty(self):
        expr = BindingExpression(self.person, u'birthYear')
        eq_(expr.getValue(), 1970)

    def testReadCompoundProperty(self):
        expr = BindingExpression(
            self.person, u'"%s %s, %s" % (firstName, lastName, birthYear)')
        eq_(expr.getValue(), u'Joe Average, 1970')

    def testWriteSimpleProperty(self):
        expr = BindingExpression(self.person, u'birthYear')
        expr.setValue(1980)
        eq_(self.person.birthYear, 1980)


class TestBinding(object):
    def setup(self):
        self.person = Person(u'Joe', u'Average', 1970)
        self.dummy = DummyObject()
        self.group = BindingGroup(logger=logging.getLogger(__name__))

    def teardown(self):
        self.group.unbind()

    def testManualSync(self):
        self.group.bind(self.person,
                        u'"%s %s, %s" % (firstName, lastName, birthYear)',
                        self.dummy, u'value', mode=MANUAL)
        eq_(self.dummy.value, None)

        self.group.sync()
        eq_(self.dummy.value, u'Joe Average, 1970')

        self.person.birthYear = 1975
        eq_(self.dummy.value, u'Joe Average, 1970')

    def testReadOnly(self):
        self.group.bind(self.person,
                        u'"%s %s, %s" % (firstName, lastName, birthYear)',
                        self.dummy, u'value')
        eq_(self.dummy.value, u'Joe Average, 1970')

        self.person.firstName = u'Mary'
        eq_(self.dummy.value, u'Mary Average, 1970')

        self.person.birthYear = 1975
        eq_(self.dummy.value, u'Mary Average, 1975')

    def testReadWrite(self):
        self.group.bind(self.person, u'birthYear', self.dummy, u'value',
                        mode=TWOWAY)

        self.person.birthYear = 1972
        eq_(self.person.birthYear, 1972)
        eq_(self.dummy.value, 1972)

        self.dummy.value = 1978
        eq_(self.person.birthYear, 1978)
        eq_(self.dummy.value, 1978)

    def testGeneratorExpr(self):
        self.group.bind(self.person, u'u" ".join(c for c in firstName)',
                        self.dummy, u'value')
        eq_(self.dummy.value, u'J o e')

        self.dummy.value = None
        self.person.c = 234
        eq_(self.dummy.value, None)

    def testListBinding(self):
        mike = Person(u'Mike', u'Average', 1995)
        sally = Person(u'Sally', u'Average', 1997)
        self.person.children = [mike, sally]
        self.group.bind(self.person, 'children[favorite].lastName',
                        self.dummy, 'value')
        eq_(self.dummy.value, None)

        self.person.favorite = 1
        eq_(self.dummy.value, u'Average')

        sally.lastName = u'Mediocre'
        eq_(self.dummy.value, u'Mediocre')

    def testCallBinding(self):
        mike = Person(u'Mike', u'Average', 1995)
        sally = Person(u'Sally', u'Average', 1997)
        self.person.children = [mike, sally]
        self.group.bind(self.person, 'getChild(favorite).lastName',
                        self.dummy, 'value')
        self.group.dump()
        eq_(self.dummy.value, None)

        self.person.favorite = 1
        eq_(self.dummy.value, u'Average')

        sally.lastName = u'Mediocre'
        eq_(self.dummy.value, u'Mediocre')


class TestAdapters(object):
    def setup(self):
        self.person = Person(u'Joe', u'Average', 1970)
        self.dummy = DummyObject()
        self.group = BindingGroup()

    def teardown(self):
        self.group.unbind()

    def testJCheckBox(self):
        check = JCheckBox()
        self.group.bind(self.person, u'firstName == u"Bob"', check,
                        u'selected')
        self.group.bind(check, u'selected', self.dummy, u'value')
        eq_(check.selected, False)
        eq_(self.dummy.value, False)

        self.person.firstName = u'Bob'
        eq_(check.selected, True)
        eq_(self.dummy.value, True)

        self.person.firstName = u'Mary'
        eq_(check.selected, False)
        eq_(self.dummy.value, False)

    def testJTextField(self):
        firstNameField = JTextField()
        lastNameField = JTextField()
        birthYearField = JFormattedTextField()
        self.group.bind(self.person, u'firstName', firstNameField,
                        u'text', mode=TWOWAY)
        self.group.bind(self.person, u'lastName', lastNameField,
                        u'text', mode=TWOWAY)
        self.group.bind(self.person, u'birthYear', birthYearField,
                        u'value', mode=TWOWAY)
        self.group.bind(self.person,
                        u'"%s %s, %s" % (firstName, lastName, birthYear)',
                        self.dummy, u'value')
        eq_(firstNameField.text, u'Joe')

        firstNameField.text = u'Mary'
        eq_(self.person.firstName, u'Mary')
        eq_(self.dummy.value, u'Mary Average, 1970')

        self.person.firstName = u'Susan'
        eq_(firstNameField.text, u'Susan')
        eq_(self.dummy.value, u'Susan Average, 1970')

        self.person.lastName = u'Mediocre'
        eq_(lastNameField.text, u'Mediocre')
        eq_(self.dummy.value, u'Susan Mediocre, 1970')

    def testJList(self):
        personList = [self.person]
        personList.append(Person(u'Mary', u'Mediocre', 1970))
        personList.append(Person(u'Bob', u'Mediocre', 1972))

        listModel = DelegateListModel(personList)
        jlist = JList(listModel)
        self.group.bind(jlist, u'selectedValue.firstName', self.dummy,
                        u'value')

        jlist.selectedIndex = 1
        eq_(jlist.selectedValue, personList[1])
        eq_(self.dummy.value, u'Mary')

        jlist.selectedIndex = 2
        eq_(jlist.selectedValue, personList[2])
        eq_(self.dummy.value, u'Bob')

        jlist.setSelectedValue(self.person, False)
        eq_(jlist.selectedIndex, 0)
        eq_(self.dummy.value, u'Joe')

    def testJTableRows(self):
        personList = [self.person]
        personList.append(Person(u'Mary', u'Mediocre', 1970))
        personList.append(Person(u'Bob', u'Mediocre', 1972))

        tableModel = ObjectTableModel(personList)
        table = JTable(tableModel)
        self.group.bind(table, u'selectedRows', self.dummy, u'value')

        table.setRowSelectionInterval(1, 1)
        eq_(tableModel.getSelectedObject(table), personList[1])
        eq_(self.dummy.value, array('i', [1]))

        table.setRowSelectionInterval(2, 2)
        eq_(tableModel.getSelectedObject(table), personList[2])
        eq_(self.dummy.value, array('i', [2]))

        table.setRowSelectionInterval(0, 1)
        eq_(tableModel.getSelectedObjects(table), [self.person, personList[1]])
        eq_(self.dummy.value, array('i', [0, 1]))

        table.selectionModel = DefaultListSelectionModel()
        eq_(self.dummy.value, array('i', []))

    def testJTableColumns(self):
        personList = [self.person]
        personList.append(Person(u'Mary', u'Mediocre', 1970))
        personList.append(Person(u'Bob', u'Mediocre', 1972))

        tableModel = ObjectTableModel(personList,
                                      (u'First name', String, 'firstName'),
                                      (u'Last name', String, 'lastName'),
                                      (u'Birth year', Integer, 'birthYear'))
        table = JTable(tableModel)
        self.group.bind(table, u'selectedColumns', self.dummy, u'value')

        table.setColumnSelectionInterval(1, 1)
        eq_(self.dummy.value, array('i', [1]))

        table.setColumnSelectionInterval(1, 2)
        eq_(self.dummy.value, array('i', [1, 2]))

        columnModel = DefaultTableColumnModel()
        columnModel.addColumn(TableColumn())
        columnModel.addColumn(TableColumn())
        table.setColumnModel(columnModel)

        table.setColumnSelectionInterval(0, 1)
        eq_(self.dummy.value, array('i', [0, 1]))

    def testJComboBox(self):
        personList = [self.person]
        personList.append(Person(u'Mary', u'Mediocre', 1970))
        personList.append(Person(u'Bob', u'Mediocre', 1972))
        dummy2 = DummyObject()

        comboBoxModel = DelegateComboBoxModel(personList)
        jcombobox = JComboBox(model=comboBoxModel, editable=True)
        self.group.bind(jcombobox, u'selectedItem.firstName', self.dummy,
                        u'value')
        self.group.bind(jcombobox, u'selectedItem', dummy2, u'value')

        jcombobox.selectedIndex = 1
        eq_(jcombobox.selectedItem, personList[1])
        eq_(self.dummy.value, u'Mary')

        jcombobox.selectedIndex = 2
        eq_(jcombobox.selectedItem, personList[2])
        eq_(self.dummy.value, u'Bob')

        jcombobox.selectedItem = self.person
        eq_(jcombobox.selectedIndex, 0)
        eq_(self.dummy.value, u'Joe')

        jcombobox.selectedItem = u'Test123'
        eq_(jcombobox.selectedIndex, -1)
        eq_(self.dummy.value, None)
        eq_(dummy2.value, u'Test123')

    def testJSpinner(self):
        valueDummy = DummyObject()
        nextValueDummy = DummyObject()
        prevValueDummy = DummyObject()
        spinnerModel = SpinnerNumberModel(3, 0, 5, 1)

        spinner = JSpinner(spinnerModel)
        self.group.bind(spinner, 'value', valueDummy, 'value')
        self.group.bind(spinner, 'nextValue', nextValueDummy, 'value')
        self.group.bind(spinner, 'previousValue', prevValueDummy, 'value')

        eq_(valueDummy.value, 3)
        eq_(nextValueDummy.value, 4)
        eq_(prevValueDummy.value, 2)

        spinner.setValue(5)
        eq_(valueDummy.value, 5)
        eq_(nextValueDummy.value, None)
        eq_(prevValueDummy.value, 4)

        spinner.setValue(0)
        eq_(valueDummy.value, 0)
        eq_(nextValueDummy.value, 1)
        eq_(prevValueDummy.value, None)

    def testJSlider(self):
        slider = JSlider(0, 10, 5)
        self.group.bind(slider, 'value', self.dummy, 'value')

        eq_(self.dummy.value, 5)

        slider.setValue(3)
        eq_(self.dummy.value, 3)

    def testJProgressBar(self):
        percentCompleteDummy = DummyObject()

        progressBar = JProgressBar(0, 10)
        self.group.bind(progressBar, 'value', self.dummy, 'value')
        self.group.bind(progressBar, 'percentComplete',
                        percentCompleteDummy, 'value')

        eq_(self.dummy.value, 0)
        eq_(percentCompleteDummy.value, 0)

        progressBar.setValue(2)
        eq_(self.dummy.value, 2)
        eq_(percentCompleteDummy.value, 0.2)

    def testListModel(self):
        listModel = DelegateListModel()
        self.group.bind(self.person, 'children', listModel, 'delegate')
        self.group.bind(listModel, 'listModel[-1].firstName', self.dummy,
                        'value', vars={'listModel': listModel})

        mike = Person(u'Mike', u'Average', 1995)
        listModel.append(mike)

        eq_(self.person.children, [mike])
        eq_(self.dummy.value, u'Mike')

        sally = Person(u'Sally', u'Average', 1997)
        listModel.append(sally)

        eq_(self.person.children, [mike, sally])
        eq_(self.dummy.value, u'Sally')
