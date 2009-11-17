"""
This module lets you synchronize properties between two objects.

The adapter objects returned by the binding methods store their endpoints
using weak references, and automatically sever the connection if either side is
garbage collected.

"""
from types import MethodType

from java.beans import PropertyChangeListener
from java.awt.event import ItemListener, FocusListener
from javax.swing import JFormattedTextField

from swingutils.beans import JavaBeanSupport
from swingutils.events import addPropertyListener

__all__ = ('ValueHolder', 'bindProperty', 'bindCheckbox', 'bindComboBox',
           'bindTextComponent')


class ValueHolder(JavaBeanSupport):
    """
    Holds a single value and fires a property change event every time
    that value is changed. Also mirrors the properties of the held object,
    firing property change events when it receives such events from that
    object.

    """
    _value = None
    __wrapper = None

    def __init__(self, initial=None):
        self.value = initial

    def __getattr__(self, name):
        return getattr(self._value, name)

    def __setattr__(self, name, value):
        if name in dir(self):
            object.__setattr__(self, name, value)
        else:
            setattr(self._value, name, value)
    
    def __nonzero__(self):
        return self._value is not None

    def _getvalue(self):
        return self._value

    def __delegatePropertyChange(self, event):
        self.firePropertyChange(event.propertyName, event.oldValue,
                                event.newValue)

    def _getProperties(self, value):
        return [p for p in dir(value) if not p.startswith('_')]

    def _setvalue(self, newValue):
        oldValue = self._value
        if oldValue and self.__wrapper:
            oldValue.removePropertyChangeListener(self.__wrapper)

        self._value = newValue
        self.firePropertyChange('value', oldValue, newValue)

        if hasattr(newValue, 'addPropertyChangeListener'):
            self.__wrapper = addPropertyListener(newValue, None,
                                                 self.__delegatePropertyChange)

        # Notify listeners of changes in all properties, including properties
        # from both the old and new values
        oldProps = set(self._getProperties(oldValue))
        newProps = set(self._getProperties(newValue))
        properties = oldProps.union(newProps)
        properties.discard('value')
        for property in properties:
            oldVal = getattr(oldValue, property, None)
            newVal = getattr(newValue, property, None)
            if not isinstance(oldVal, MethodType) and not \
                isinstance(newVal, MethodType):
                self.firePropertyChange(property, oldVal, newVal)

    value = property(_getvalue, _setvalue)

    def addValueListener(self, listener, *args, **kwargs):
        addPropertyListener(self, 'value', listener, *args, **kwargs)

    def removeValueListener(self, listener):
        self.removePropertyChangeListener('value', listener)


class PropertyAdapter(PropertyChangeListener):
    def __init__(self, source, srcProperty, destination, dstProperty,
                 converter, backConverter):
        self.source = source
        self.srcProperty = srcProperty
        self.destination = destination
        self.dstProperty = dstProperty
        self.converter = converter
        self.backConverter = backConverter
        self._propertyChangeInProgress = False

    def propertyChange(self, event):
        if self._propertyChangeInProgress:
            return
        self._propertyChangeInProgress = True

        src = self.source
        srcProperty = self.srcProperty
        dst = self.destination
        dstProperty = self.dstProperty
        converter = self.converter
        if event.source is dst:
            dst = src
            src = self.destination
            srcProperty = self.dstProperty
            dstProperty = self.srcProperty
            converter = self.backConverter
        
        try:
            value = getattr(src, srcProperty)
            if converter:
                value = converter(value)
            setattr(dst, dstProperty, value)
        finally:
            self._propertyChangeInProgress = False

    def disconnect(self):
        src = self.source()
        if src:
            src.removePropertyChangeListener(self)

        dst = self.destination()
        if dst:
            dst.removePropertyChangeListener(self)


class CheckBoxAdapter(PropertyChangeListener, ItemListener):
    def __init__(self, holder, srcProperty, checkBox, converter,
                 backConverter):
        self.holder = holder
        self.srcProperty = srcProperty
        self.checkBox = checkBox
        self.converter = converter
        self.backConverter = backConverter

    def propertyChange(self, event):
        src = self.holder()
        checkBox = self.checkBox()
        value = getattr(src, self.srcProperty)
        value = self.converter(value)
        checkBox.selected = value
        self.checkBox.enabled = self.holder.value is not None

    def stateChanged(self, event):
        src = self.holder()
        checkBox = self.checkBox()
        value = self.backConverter(checkBox.selected)
        setattr(src, self.srcProperty, value)

    def disconnect(self):
        self.holder.removePropertyChangeListener(self)
        self.checkBox.removeItemListener(self)


class ComboBoxAdapter(PropertyChangeListener, ItemListener):
    def __init__(self, holder, srcProperty, comboBox, converter,
                 backConverter):
        self.holder = holder
        self.srcProperty = srcProperty
        self.comboBox = comboBox
        self.converter = converter
        self.backConverter = backConverter

    def propertyChange(self, event):
        value = getattr(self.holder, self.srcProperty)
        value = self.converter(value)
        self.comboBox.selectedItem = value
        self.comboBox.enabled = self.holder.value is not None

    def stateChanged(self, event):
        value = self.backConverter(event.item)
        setattr(self.holder, self.srcProperty, value)

    def disconnect(self):
        self.holder.removePropertyChangeListener(self)
        self.comboBox.removeItemListener(self)


class TextComponentAdapter(PropertyChangeListener, FocusListener):
    def __init__(self, holder, srcProperty, textComponent):
        self.holder = holder
        self.srcProperty = srcProperty
        self.textComponent = textComponent

    def propertyChange(self, event):
        self.textComponent.text = event.newValue
        self.textComponent.enabled = self.holder.value is not None

    def focusLost(self, event):
        setattr(self.holder, self.srcProperty, self.textComponent.text)

    def disconnect(self):
        self.holder.removePropertyChangeListener(self)
        self.textComponent.removeFocusListener(self)


class FormattedTextFieldAdapter(PropertyAdapter):
    def __init__(self, holder, srcProperty, textField):
        PropertyAdapter.__init__(self, holder, srcProperty, textField, 'value',
                                 None, None)

    def propertyChange(self, event):
        PropertyAdapter.propertyChange(self, event)
        self.destination.enabled = self.source.value is not None


def bindProperty(source, srcProperty, destination, dstProperty,
                 twoway=False, syncnow=False, converter=None,
                 backConverter=None):
    """
    Connects a property in the source object to a property in the destination
    object. When the source property changes, the destination property is set
    to the same value.

    It is also possible to modify the value being passed to the destination
    object by specifying a converter function. This callable receives the value
    from the source property, and should return the value that will be set as
    the the value of the destination property.

    :param twoway: if `True`, changes in the destination property are also
                   propagated to the source property
    :param syncnow: if `True`, the value of the source property is copied to
                    the destination property before this call returns.
    :param converter: callable that receives the source value and returns
                      the value that should be passed to the destination
                      object
    :param converter: callable that receives the destination value and returns
                      the value that should be passed to the source
                      object when `twoway` is `True`
    :return: listener adapter that you can use to break the connection
             between the two objects

    """
    assert hasattr(source, srcProperty), \
        'source object has no property named "%s"' % srcProperty
    assert hasattr(destination, dstProperty), \
        'destination object has no property named "%s"' % dstProperty
    assert hasattr(source, 'addPropertyChangeListener'), \
        'source object has no addPropertyChangeListener method'
    if twoway:
        assert hasattr(destination, 'addPropertyChangeListener'), \
            'destination object has no addPropertyChangeListener method'

    adapter = PropertyAdapter(source, srcProperty, destination, dstProperty,
                              converter, backConverter)
    source.addPropertyChangeListener(srcProperty, adapter)
    if twoway:
        destination.addPropertyChangeListener(dstProperty, adapter)

    if syncnow:
        value = getattr(source, srcProperty)
        setattr(destination, dstProperty, value)

    return adapter


def bindCheckbox(holder, srcProperty, checkBox, twoway=True):
    """
    Binds an object to a check box.
    
    :param checkBox: the check box to bind to
    :param twoway: `True` if changes in the check box state should also reflect
                   in `holder`
    :type checkBox: :class:`javax.swing.JCheckBox`
    
    """
    adapter = CheckBoxAdapter(holder, srcProperty, checkBox)
    holder.addPropertyChangeListener(srcProperty, adapter)
    if twoway:
        checkBox.addItemListener(adapter)
    checkBox.enabled = holder.value is not None


def bindComboBox(holder, srcProperty, comboBox, twoway=True,
                 converter=None, backConverter=None):
    adapter = ComboBoxAdapter(holder, srcProperty, comboBox, converter,
                              backConverter)
    holder.addPropertyChangeListener(srcProperty, adapter)
    if twoway:
        comboBox.addItemListener(adapter)
    comboBox.enabled = holder.value is not None


def bindTextComponent(holder, srcProperty, textComponent, twoway=True):
    if isinstance(textComponent, JFormattedTextField):
        adapter = FormattedTextFieldAdapter(holder, srcProperty, textComponent)
        holder.addPropertyChangeListener(srcProperty, adapter)
        if twoway:
            textComponent.addPropertyChangeListener('value', adapter)
    else:
        adapter = TextComponentAdapter(holder, srcProperty, textComponent)
        holder.addPropertyChangeListener(srcProperty, adapter)
        if twoway:
            textComponent.addFocusListener(adapter)
    textComponent.enabled = holder.value is not None
