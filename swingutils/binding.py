"""This module lets you synchronize properties between two objects."""
from javax.swing import JFormattedTextField
import weakref

from java.beans import PropertyChangeListener
from java.awt.event import ItemListener, FocusListener

from swingutils.beans import JavaBeanSupport
from swingutils.events import addPropertyListener, addItemListener

__all__ = ('ValueHolder', 'BeanHolder', 'PropertyAdapter', 'connect')


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

    def _getvalue(self):
        return self._value

    def __delegatePropertyChange(self, event):
        self.firePropertyChange(event.propertyName, event.oldValue,
                                event.newValue)

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
        oldProps = set([p for p in dir(oldValue) if not p.startswith('_')])
        newProps = set([p for p in dir(newValue) if not p.startswith('_')])
        properties = oldProps.union(newProps)
        properties.discard('value')
        for property in properties:
            oldVal = getattr(oldValue, property, None)
            newVal = getattr(newValue, property, None)
            self.firePropertyChange(property, oldVal, newVal)

    value = property(_getvalue, _setvalue)

    def addValueListener(self, listener, *args, **kwargs):
        addPropertyListener(self, 'value', listener, *args, **kwargs)

    def removeValueListener(self, listener):
        self.removePropertyChangeListener('value', listener)


class PropertyAdapter(PropertyChangeListener):
    def __init__(self, source, destination, converter, backConverter):
        self.source = weakref.ref(source, self.disconnect)
        self.destination = weakref.ref(destination, self.disconnect)
        self.converter = converter
        self.backConverter = backConverter

    def propertyChange(self, event):
        src = self.source()
        dst = self.destination()
        converter = self.converter
        if event.source is dst:
            dst = src
            src = self.destination()
            converter = self.backConverter
        value = getattr(src, event.propertyName)
        value = converter(value)
        setattr(dst, event.propertyName, value)

    def disconnect(self, ref=None):
        src = self.source()
        if src:
            src.removePropertyChangeListener(self)

        dst = self.destination()
        if dst:
            dst.removePropertyChangeListener(self)


class CheckBoxAdapter(PropertyChangeListener, ItemListener):
    def __init__(self, source, srcProperty, checkBox, converter,
                 backConverter):
        self.source = weakref.ref(source, self.disconnect)
        self.srcProperty = srcProperty
        self.checkBox = weakref.ref(checkBox, self.disconnect)
        self.converter = converter
        self.backConverter = backConverter

    def propertyChange(self, event):
        src = self.source()
        checkBox = self.checkBox()
        value = getattr(src, self.srcProperty)
        value = self.converter(value)
        checkBox.selected = value

    def stateChanged(self, event):
        src = self.source()
        checkBox = self.checkBox()
        value = self.backConverter(checkBox.selected)
        setattr(src, self.srcProperty, value)

    def disconnect(self, ref=None):
        src = self.source()
        if src:
            src.removePropertyChangeListener(self)

        checkBox = self.checkBox()
        if checkBox:
            checkBox.removeItemListener(self)


class ComboBoxAdapter(PropertyChangeListener, ItemListener):
    def __init__(self, source, srcProperty, comboBox, converter,
                 backConverter):
        self.source = weakref.ref(source, self.disconnect)
        self.srcProperty = srcProperty
        self.comboBox = weakref.ref(comboBox, self.disconnect)
        self.converter = converter
        self.backConverter = backConverter

    def propertyChange(self, event):
        src = self.source()
        combo = self.comboBox()
        value = getattr(src, self.srcProperty)
        value = self.converter(value)
        combo.selectedItem = value

    def stateChanged(self, event):
        value = self.backConverter(event.item)
        setattr(self.source, self.srcProperty, value)

    def disconnect(self, ref=None):
        src = self.source()
        if src:
            src.removePropertyChangeListener(self)

        combo = self.comboBox()
        if combo:
            combo.removeItemListener(self)


class TextComponentAdapter(PropertyChangeListener, FocusListener):
    def __init__(self, source, srcProperty, textComponent):
        self.source = weakref.ref(source, self.disconnect)
        self.srcProperty = srcProperty
        self.textComponent = weakref.ref(textComponent, self.disconnect)

    def propertyChange(self, event):
        src = self.source()
        textComponent = self.textComponent()
        value = getattr(src, self.srcProperty)
        textComponent.text = value

    def focusLost(self, event):
        src = self.source()
        textComponent = self.textField()
        setattr(src, self.srcProperty, textComponent.text)


def bindProperty(source, srcProperty, destination, dstProperty,
                 twoway=False, syncNow=False, converter=lambda v: v,
                 backConverter=lambda v: v):
    """
    Connects a property in the source object to a property in the destination
    object. When the source property changes, the destination property is set
    to the same value.
    
    It is also possible to modify the value being passed to the destination
    object by specifying a converter function. This callable receives the value
    from the source property, and should return the value that will be set as
    the the value of the destination property.

    The :class:`~PropertyAdapter` that binds the two properties only stores
    weak references to the source and destination objects, and automatically
    severs the connection if either side is garbage collected.

    :param twoway: if `True`, changes in the destination property are also
                   propagated to the source property
    :param syncNow: if `True`, the value of the source property is copied to
                    the destination property before this call returns.
    :param converter: callable that receives the source value and returns
                      the value that should be passed to the destination
                      object
    :return: listener adapter that you can use to break the connection
             between the two objects
    :rtype: :class:`PropertyAdapter`

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

    adapter = PropertyAdapter(source, destination, converter, backConverter)
    source.addPropertyChangeListener(srcProperty, adapter)
    if twoway:
        destination.addPropertyChangeListener(dstProperty, adapter)

    if syncNow:
        value = getattr(source, srcProperty)
        setattr(destination, dstProperty, value)

    return adapter


def bindCheckbox(source, srcProperty, checkBox, twoway=True):
    adapter = CheckBoxAdapter(source, srcProperty, checkBox)

    source.addPropertyChangeListener(srcProperty, adapter)
    if twoway:
        addItemListener(checkBox, adapter)


def bindComboBox(source, srcProperty, comboBox, twoway=True,
                 converter=lambda v: v, backConverter=lambda v: v):
    adapter = ComboBoxAdapter(source, srcProperty, comboBox, converter,
                              backConverter)
    source.addPropertyChangeListener(srcProperty, adapter)
    if twoway:
        addItemListener(comboBox, adapter)


def bindTextComponent(source, srcProperty, textComponent, twoway=True):
    if isinstance(textComponent, JFormattedTextField):
        bindProperty(source, srcProperty, textComponent, 'value', twoway)
    else:
        adapter = TextComponentAdapter(source, srcProperty, textComponent)
        source.addPropertyChangeListener(srcProperty, adapter)
        if twoway:
            textComponent.addFocusListener(adapter)


def bindFormattedTextField(source, srcProperty, textField, twoway=True):
    bindProperty(source, srcProperty, textField, 'value', twoway)
