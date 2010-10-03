Text field formatters
=====================

Formatters are used with :class:`~javax.swing.JFormattedTextField` components
to convert textual input into other types of objects, including numbers.
When you build your UIs programmatically the easiest way to install formatters
is to supply them to JFormattedTextField's constructor as arguments::

    from javax.swing import JFormattedTextField
    from java.text import DecimalFormat

    someNumericField = JFormattedTextField(DecimalFormat('0.00'))

However, when you build your UI declaratively, like with UI designer tools such
as JFormDesigner, you cannot change the way the fields are instantiated. This
module lets you easily install formats in formatted text fields afterwards.

This example installs a date format in a formatted text field using
:func:`~swingutils.format.installFormat`::

    from java.text import SimpleDateFormat
    from swingutils.format import installFormat

    installFormat(startDateField, SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSZ"))


Numeric formatters
------------------

When formatting numbers, you often want to specify the minimum and maximum
number of digits before and after the decimal point. For this reason, the
formatting module offers the :func:`~swingutils.format.installNumberFormat`
function::

    from java.lang import Double
    from swingutils.format import installNumberFormat

    installNumberFormat(someNumericField, Double, maximumFractionDigits=2)

If you give a Python numeric type as the ``type`` parameter, it will pick the
corresponding Java numeric type as the output type according to the following
table:

============ ==========
Python type  Java type
============ ==========
int          Long
long         BigInteger
float        Double
decimal      BigDecimal
============ ==========
