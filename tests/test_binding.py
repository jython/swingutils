from nose.tools import eq_, raises

from javax.swing import JTextField, JFormattedTextField, JList, JComboBox,\
    SpinnerNumberModel, JSpinner

from swingutils.binding import BindingGroup, BindingExpression, \
    BindingWriteError, READ_WRITE, READ_ONCE
from swingutils.beans import AutoChangeNotifier
from swingutils.models.list import DelegateListModel
from swingutils.models.combobox import DelegateComboBoxModel


class Person(AutoChangeNotifier):
    def __init__(self, firstName=None, lastName=None, birthYear=None):
        self.firstName = firstName
        self.lastName = lastName
        self.birthYear = birthYear


class DummyObject(AutoChangeNotifier):
    value = None


class TestExpressions(object):
    def setup(self):
        self.person = Person(u'Joe', u'Average', 1970)

    def testReadSimpleProperty(self):
        expr = BindingExpression.parse(u'${birthYear}', {})
        value = expr.getValue(self.person)
        eq_(value, 1970)

    def testReadCompoundProperty(self):
        expr = BindingExpression.parse(
            u'${firstName} ${lastName}, ${birthYear}', {})
        eq_(expr.getValue(self.person), u'Joe Average, 1970')

    def testReadJoinedProperty(self):
        expr1 = BindingExpression.parse(u'${firstName} ', {})
        expr2 = BindingExpression.parse(u'${lastName}, ', {})
        expr3 = BindingExpression.parse(u'${birthYear}', {})
        expr = expr1 + expr2 + expr3
        eq_(expr.getValue(self.person), u'Joe Average, 1970')

    def testWriteSimpleProperty(self):
        expr = BindingExpression.parse(u'${birthYear}', {})
        expr.setValue(self.person, 1980)
        eq_(self.person.birthYear, 1980)

    @raises(BindingWriteError)
    def testWriteCompoundProperty(self):
        expr = BindingExpression.parse(
            u'${firstName} ${lastName}, ${birthYear}', {})
        expr.setValue(self.person, u'Joe Average, 1980')


class TestBinding(object):
    def setup(self):
        self.person = Person(u'Joe', u'Average', 1970)
        self.dummy = DummyObject()
        self.group = BindingGroup()

    def teardown(self):
        self.group.unbind()

    def testReadOnce(self):
        self.group.bind(self.person, u'${firstName} ${lastName}, ${birthYear}',
                        self.dummy, u'${value}', mode=READ_ONCE)

        eq_(self.dummy.value, u'Joe Average, 1970')

        self.person.birthYear = 1975
        eq_(self.dummy.value, u'Joe Average, 1970')

    def testReadOnly(self):
        self.group.bind(self.person, u'${firstName} ${lastName}, ${birthYear}',
                        self.dummy, u'${value}')

        self.person.firstName = u'Mary'
        eq_(self.dummy.value, u'Mary Average, 1970')

        self.person.birthYear = 1975
        eq_(self.dummy.value, u'Mary Average, 1975')

    def testReadWrite(self):
        self.group.bind(self.person, u'${birthYear}', self.dummy, u'${value}',
                        mode=READ_WRITE)

        self.person.birthYear = 1972
        eq_(self.person.birthYear, 1972)
        eq_(self.dummy.value, 1972)

        self.dummy.value = 1978
        eq_(self.person.birthYear, 1978)
        eq_(self.dummy.value, 1978)

    def testJTextField(self):
        firstNameField = JTextField()
        lastNameField = JTextField()
        birthYearField = JFormattedTextField()
        self.group.bind(self.person, u'${firstName}', firstNameField,
                        u'${text}', mode=READ_WRITE)
        self.group.bind(self.person, u'${lastName}', lastNameField,
                        u'${text}', mode=READ_WRITE)
        self.group.bind(self.person, u'${birthYear}', birthYearField,
                        u'${value}', mode=READ_WRITE)
        self.group.bind(self.person, u'${firstName} ${lastName}, ${birthYear}',
                        self.dummy, u'${value}')
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
        self.group.bind(jlist, u'${selectedValue.firstName}', self.dummy,
                        u'${value}')

        jlist.selectedIndex = 1
        eq_(jlist.selectedValue, personList[1])
        eq_(self.dummy.value, u'Mary')

        jlist.selectedIndex = 2
        eq_(jlist.selectedValue, personList[2])
        eq_(self.dummy.value, u'Bob')

        jlist.setSelectedValue(self.person, False)
        eq_(jlist.selectedIndex, 0)
        eq_(self.dummy.value, u'Joe')

    def testJComboBox(self):
        personList = [self.person]
        personList.append(Person(u'Mary', u'Mediocre', 1970))
        personList.append(Person(u'Bob', u'Mediocre', 1972))
        dummy2 = DummyObject()

        comboBoxModel = DelegateComboBoxModel(personList)
        jcombobox = JComboBox(model=comboBoxModel, editable=True)
        self.group.bind(jcombobox, u'${selectedItem.firstName}', self.dummy,
                        u'${value}')
        self.group.bind(jcombobox, u'${selectedItem}', dummy2, u'${value}')

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
        self.group.bind(spinner, '${value}', valueDummy, '${value}')
        self.group.bind(spinner, '${nextValue}', nextValueDummy, '${value}')
        self.group.bind(spinner, '${previousValue}', prevValueDummy, '${value}')

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
