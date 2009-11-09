"""This module lets you synchronize properties between two objects."""
import weakref

from java.beans import PropertyChangeListener

__all__ = ('connect',)


class PropertyAdapter(PropertyChangeListener):
    def __init__(self, source, destination, converter):
        self.source_ref = weakref.ref(source, self.disconnect)
        self.destination_ref = weakref.ref(destination, self.disconnect)
        self.converter = converter

    def propertyChange(self, event):
        src = self.source_ref()
        dst = self.destination_ref()
        if event.source is dst:
            dst = src
            src = self.destination_ref()
        value = getattr(src, event.propertyName)
        if self.converter:
            value = self.converter(value)
        setattr(dst, event.propertyName, value)

    def disconnect(self, ref=None):
        src = self.source_ref()
        if src:
            src.removePropertyChangeListener(self)

        dst = self.destination_ref()
        if dst:
            dst.removePropertyChangeListener(self)


def connect(source, srcProperty, destination, dstProperty, twoway=False,
            syncNow=False, converter=None):
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
        assert not converter, 'twoway and converter are mutually exclusive'

    adapter = PropertyAdapter(source, destination, converter)
    source.addPropertyChangeListener(srcProperty, adapter)
    if twoway:
        destination.addPropertyChangeListener(dstProperty, adapter)

    if syncNow:
        value = getattr(source, srcProperty)
        setattr(destination, dstProperty, value)

    return adapter
