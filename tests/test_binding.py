from nose.tools import eq_, raises

from swingutils.binding import BindingGroup, BindingExpression,\
    CompoundWriteError
from swingutils.beans import AutoChangeNotifier


class Person(AutoChangeNotifier):
    def __init__(self, firstName, lastName, birthYear):
        self.firstName = firstName
        self.lastName = lastName
        self.birthYear = birthYear


class TestExpressions(object):
    def setup(self):
        self.person = Person(u'Joe', u'Average', 1970)

    def testReadSimpleProperty(self):
        expr = BindingExpression(self.person, u'${birthYear}')
        value = expr.getValue()
        assert type(value) == int
        eq_(value, 1970)

    def testReadCompoundProperty(self):
        expr = BindingExpression(self.person,
            u'${firstName} ${lastName}, ${birthYear}')
        eq_(expr.getValue(), u'Joe Average, 1970')

    def testWriteSimpleProperty(self):
        expr = BindingExpression(self.person, u'${birthYear}')
        expr.setValue(1980)
        eq_(self.person.birthYear, 1980)

    @raises(CompoundWriteError)
    def testWriteCompoundProperty(self):
        expr = BindingExpression(self.person,
            u'${firstName} ${lastName}, ${birthYear}')
        expr.setValue(u'Joe Average, 1980')

#p = BindingProperty(person, '${birthYear}')
#assert p.evaluate() == 1979
#
#p = BindingProperty(person, '${{"test": 9}}')
#assert p.evaluate() == dict(test=9)
