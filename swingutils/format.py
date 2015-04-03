"""
Contains convenience functions for working with formatters.

"""
from __future__ import unicode_literals
from decimal import Decimal

from java.lang import Number, Long, Double
from java.math import BigDecimal, BigInteger
from java.text import DecimalFormat, DateFormat, NumberFormat, Format
from javax.swing.text import (DefaultFormatterFactory, InternationalFormatter,
                              DateFormatter, NumberFormatter)

_TYPES_MAP = {int: Long,
              long: BigInteger,
              float: Double,
              Decimal: BigDecimal}


class PyDecimalFormat(DecimalFormat):
    def __init__(self, pattern=None, integerDigits=None, fractionDigits=None,
                 **kwargs):
        if integerDigits is not None:
            kwargs['maximumIntegerDigits'] = integerDigits
            kwargs['minimumIntegerDigits'] = integerDigits
        if fractionDigits is not None:
            kwargs['maximumFractionDigits'] = fractionDigits
            kwargs['minimumFractionDigits'] = fractionDigits

        if pattern is not None:
            DecimalFormat.__init__(self, pattern, **kwargs)
        else:
            DecimalFormat.__init__(self, **kwargs)


class EmptyNumberFormatter(NumberFormatter):
    def stringToValue(self, text):
        return NumberFormatter.stringToValue(self, text) if text else None


def installFormat(field, format):
    """
    Installs a Format in a JFormattedTextField.

    :param field: the field to install the format to
    :type field: :class:`~javax.swing.JFormattedTextField`
    :param format: the format to install
    :type format: :class:`~java.text.Format`

    """
    formatter = None
    if isinstance(format, DateFormat):
        formatter = DateFormatter(format)
    elif isinstance(format, NumberFormat):
        formatter = NumberFormatter(format)
    elif isinstance(format, Format):
        formatter = InternationalFormatter(format)
    else:
        raise TypeError('format must be an instance of java.text.Format')

    field.formatterFactory = DefaultFormatterFactory(formatter)


def installNumberFormat(field, type=None, nullable=False, **kwargs):
    """
    Installs a number formatter in a JFormattedTextField.

    :param field: the field to install the format to
    :type field: :class:`~javax.swing.JFormattedTextField`
    :param type: a subclass of :class:`~java.lang.Number` or a python numeric
                 type
    :param kwargs: attribute values to set on the PyDecimalFormat

    """
    type = _TYPES_MAP.get(type, type)
    if type:
        if not issubclass(type, Number):
            raise TypeError('type must be a numeric type')

    format = PyDecimalFormat(**kwargs)
    if nullable:
        formatter = EmptyNumberFormatter(format, valueClass=type)
    else:
        formatter = NumberFormatter(format, valueClass=type)
    field.formatterFactory = DefaultFormatterFactory(formatter)
