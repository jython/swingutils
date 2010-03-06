from java.lang import Number, Integer, Long, Double
from java.text import DecimalFormat, DateFormat, NumberFormat, Format
from javax.swing.text import DefaultFormatterFactory, InternationalFormatter, \
    DateFormatter, NumberFormatter


_TYPES_MAP = {int: Integer, long: Long, float: Double}

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


def installFormat(field, format):
    """
    Installs a Format in a JFormattedTextField.

    :type field: :class:`javax.swing.JFormattedTextField`
    :type format: :class:`java.text.Format`

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


def installNumberFormat(field, type=None, **kwargs):
    """
    Installs a number formatter in a JFormattedTextField.

    :type field: :class:`javax.swing.JFormattedTextField`
    :param type: a subclass of :class:`java.lang.Number` or a python numeric
                 type
    :param kwargs: attribute values to set on the PyDecimalFormat
    
    """
    format = PyDecimalFormat(valueClass=type, **kwargs)
    formatter = NumberFormatter(format)

    type = _TYPES_MAP.get(type, type)
    if type:
        if not issubclass(type, Number):
            raise TypeError('type must be a numeric type')
        formatter.valueClass = type

    field.formatterFactory = DefaultFormatterFactory(formatter)
