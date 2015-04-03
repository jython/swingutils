from decimal import Decimal

from java.lang import Short, Integer, Long, Double, Float
from java.text import SimpleDateFormat, DecimalFormatSymbols
from java.util import Date, GregorianCalendar
from java.math import BigDecimal
from javax.swing import JFormattedTextField

from swingutils.format import (installNumberFormat, installFormat,
                               PyDecimalFormat)


DECIMAL_SEPARATOR = DecimalFormatSymbols().decimalSeparator


def testDateFormat():
    textField = JFormattedTextField()
    installFormat(textField, SimpleDateFormat('yyyy-MM-dd'))
    textField.setText(u'2010-11-9')
    textField.commitEdit()
    assert type(textField.value) == Date

    cal = GregorianCalendar(time=textField.value)
    assert cal.get(GregorianCalendar.YEAR) == 2010
    assert cal.get(GregorianCalendar.MONTH) == 10   # January = 0
    assert cal.get(GregorianCalendar.DAY_OF_MONTH) == 9


def testFractionDigits():
    format = PyDecimalFormat(fractionDigits=3)
    assert format.format(123.4562) == u'123%s456' % DECIMAL_SEPARATOR
    assert format.format(123.4) == u'123%s400' % DECIMAL_SEPARATOR


def testIntegerDigits():
    format = PyDecimalFormat(integerDigits=3)
    assert format.format(12) == u'012'
    assert format.format(1234) == u'234'


def numberFormatterTest(numType, expectedType, text, nullable):
    textField = JFormattedTextField()
    installNumberFormat(textField, numType, nullable=nullable)
    textField.setText(text)
    textField.commitEdit()
    assert type(textField.value) == expectedType


def testNumberFormatters():
    for nullable in True, False:
        yield numberFormatterTest, Short, int, u'123', nullable
        yield numberFormatterTest, Integer, int, u'123', nullable
        yield numberFormatterTest, Long, long, u'123', nullable
        yield numberFormatterTest, Float, float, u'123.4', nullable
        yield numberFormatterTest, Double, float, u'123.4', nullable
        yield numberFormatterTest, int, long, u'123', nullable
        yield numberFormatterTest, long, long, u'123', nullable
        yield numberFormatterTest, Decimal, BigDecimal, u'123.4', nullable
