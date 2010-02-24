from nose.tools import eq_, raises

from swingutils.binding import BindingGroup, BindingExpression, \
    BindingWriteError, READ_WRITE, READ_ONCE
from swingutils.beans import AutoChangeNotifier
from javax.swing import JTextField, JFormattedTextField


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
        expr = BindingExpression.create(u'${birthYear}', {})
        value = expr.getValue(self.person)
        eq_(value, 1970)

    def testReadCompoundProperty(self):
        expr = BindingExpression.create(
            u'${firstName} ${lastName}, ${birthYear}', {})
        eq_(expr.getValue(self.person), u'Joe Average, 1970')

    def testReadJoinedProperty(self):
        expr1 = BindingExpression.create(u'${firstName} ', {})
        expr2 = BindingExpression.create(u'${lastName}, ', {})
        expr3 = BindingExpression.create(u'${birthYear}', {})
        expr = expr1 + expr2 + expr3
        eq_(expr.getValue(self.person), u'Joe Average, 1970')

    def testWriteSimpleProperty(self):
        expr = BindingExpression.create(u'${birthYear}', {})
        expr.setValue(self.person, 1980)
        eq_(self.person.birthYear, 1980)

    @raises(BindingWriteError)
    def testWriteCompoundProperty(self):
        expr = BindingExpression.create(
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
