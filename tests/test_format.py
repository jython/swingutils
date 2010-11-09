from java.lang import Short, Integer, Long, Double
from java.text import SimpleDateFormat, DecimalFormatSymbols
from java.util import Date, GregorianCalendar
from java.math import BigInteger
from javax.swing import JFormattedTextField

from nose.tools import eq_

from swingutils.format import installNumberFormat, installFormat,\
    PyDecimalFormat


class TestFormats(object):
    @classmethod
    def setupClass(cls):
        cls.decimalSeparator = DecimalFormatSymbols().decimalSeparator

    def setup(self):
        self.textField = JFormattedTextField()

    def testDateFormat(self):
        installFormat(self.textField, SimpleDateFormat('yyyy-MM-dd'))
        self.textField.setText(u'2010-11-9')
        self.textField.commitEdit()
        eq_(type(self.textField.value), Date)

        cal = GregorianCalendar(time=self.textField.value)
        eq_(cal.get(GregorianCalendar.YEAR), 2010)
        eq_(cal.get(GregorianCalendar.MONTH), 10)   # January = 0
        eq_(cal.get(GregorianCalendar.DAY_OF_MONTH), 9)

    def testShortFormat(self):
        installNumberFormat(self.textField, Short)
        self.textField.setText(u'123')
        self.textField.commitEdit()
        eq_(type(self.textField.value), int)

    def testIntegerFormat(self):
        installNumberFormat(self.textField, Integer)
        self.textField.setText(u'123')
        self.textField.commitEdit()
        eq_(type(self.textField.value), int)

    def testPyIntFormat(self):
        installNumberFormat(self.textField, int)
        self.textField.setText(u'123')
        self.textField.commitEdit()
        eq_(type(self.textField.value), long)

    def testLongFormat(self):
        installNumberFormat(self.textField, Long)
        self.textField.setText(u'123')
        self.textField.commitEdit()
        eq_(type(self.textField.value), long)

    def testPyLongFormat(self):
        installNumberFormat(self.textField, long)
        self.textField.setText(u'123')
        self.textField.commitEdit()
        eq_(type(self.textField.value), BigInteger)

    def testDoubleFormat(self):
        installNumberFormat(self.textField, Double)
        self.textField.setText(u'123%s4' % self.decimalSeparator)
        self.textField.commitEdit()
        eq_(type(self.textField.value), float)
        eq_(self.textField.value, 123.4)

    def testPyFloatFormat(self):
        installNumberFormat(self.textField, float)
        self.textField.setText(u'123%s4' % self.decimalSeparator)
        self.textField.commitEdit()
        eq_(type(self.textField.value), float)
        eq_(self.textField.value, 123.4)

    def testFractionDigits(self):
        format = PyDecimalFormat(fractionDigits=3)
        eq_(format.format(123.4562), u'123%s456' % self.decimalSeparator)
        eq_(format.format(123.4), u'123%s400' % self.decimalSeparator)

    def testIntegerDigits(self):
        format = PyDecimalFormat(integerDigits=3)
        eq_(format.format(12), u'012')
        eq_(format.format(1234), u'234')
