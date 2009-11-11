from nose.tools import eq_

from swingutils.beans import AutoChangeNotifier
from swingutils.binding import ValueHolder, bindProperty
from swingutils.events import addPropertyListener


class TestValueHolder(object):
    def setup(self):
        self.holder = ValueHolder()
        self.bean1 = AutoChangeNotifier()
        self.bean2 = AutoChangeNotifier()
        self.bean3 = AutoChangeNotifier()
        self.bean1.prop1 = 'testVal1'
        self.bean2.prop1 = 'testVal2'
        self.bean3.prop2 = 'testVal3'

    def testSetHolder(self):
        self.holder.value = self.bean1
        eq_(self.holder.prop1, 'testVal1')

        self.holder.value = self.bean2
        eq_(self.holder.prop1, 'testVal2')

    def testValueChange(self):
        def listener(event, listenerResult):
            listenerResult[0] = event

        listenerResult = [None]
        self.holder.addValueListener(listener, listenerResult)

        self.holder.value = self.bean1
        event = listenerResult[0]
        eq_(event.propertyName, 'value')
        eq_(event.oldValue, None)
        eq_(event.newValue, self.bean1)

        self.holder.value = self.bean2
        event = listenerResult[0]
        eq_(event.propertyName, 'value')
        eq_(event.oldValue, self.bean1)
        eq_(event.newValue, self.bean2)

    def testBeanSwitch(self):
        self.holder.value = self.bean1
        eq_(self.holder.value, self.bean1)
        eq_(self.holder.prop1, 'testVal1')

        self.holder.value = self.bean2
        eq_(self.holder.value, self.bean2)
        eq_(self.holder.prop1, 'testVal2')

    def testBeanChangeEvents(self):
        def listener(event, listenerResult):
            listenerResult[0] = event

        listenerResult1 = [None]
        listenerResult2 = [None]
        addPropertyListener(self.holder, 'prop1', listener, listenerResult1)
        addPropertyListener(self.holder, 'prop2', listener, listenerResult2)

        self.holder.value = self.bean1
        event = listenerResult1[0]
        eq_(event.oldValue, None)
        eq_(event.newValue, 'testVal1')

        self.holder.value = self.bean3
        event1 = listenerResult1[0]
        event2 = listenerResult2[0]
        eq_(event1.oldValue, 'testVal1')
        eq_(event1.newValue, None)
        eq_(event2.oldValue, None)
        eq_(event2.newValue, 'testVal3')

    def testPropertyChange1(self):
        """Test that passing a property change to the underlying value works"""
        def listener(event, listenerResult):
            listenerResult[0] = event

        listenerResult = [None]
        self.holder.value = self.bean1
        addPropertyListener(self.bean1, 'prop1', listener, listenerResult)

        self.holder.prop1 = 'anotherValue'
        event = listenerResult[0]
        eq_(event.propertyName, 'prop1')
        eq_(event.oldValue, 'testVal1')
        eq_(event.newValue, 'anotherValue')
        eq_(self.bean1.prop1, 'anotherValue')

    def testPropertyChange2(self):
        """
        Test that changing a property on the underlying value causes a
        property change event to be fired on the holder.

        """
        def listener(event, listenerResult):
            listenerResult[0] = event

        listenerResult = [None]
        self.holder.value = self.bean1
        addPropertyListener(self.holder, 'prop1', listener, listenerResult)

        self.bean1.prop1 = 'anotherValue'
        event = listenerResult[0]
        eq_(event.propertyName, 'prop1')
        eq_(event.oldValue, 'testVal1')
        eq_(event.newValue, 'anotherValue')
        eq_(self.holder.prop1, 'anotherValue')


class TestConnect(object):
    def setup(self):
        self.bean1 = AutoChangeNotifier()
        self.bean2 = AutoChangeNotifier()
        self.bean1.prop1 = 'testVal1'
        self.bean2.prop1 = 'testVal2'

    def testOneWayNoSync(self):
        bindProperty(self.bean1, 'prop1', self.bean2, 'prop1')

        # Nothing should've changed yet
        eq_(self.bean1.prop1, 'testVal1')
        eq_(self.bean2.prop1, 'testVal2')

        # The change should propagate to bean2
        self.bean1.prop1 = 'testVal3'
        eq_(self.bean1.prop1, 'testVal3')
        eq_(self.bean2.prop1, 'testVal3')

    def testOneWaySync(self):
        bindProperty(self.bean1, 'prop1', self.bean2, 'prop1',
                          syncNow=True)

        # Bean2.prop1 should have changed
        eq_(self.bean1.prop1, 'testVal1')
        eq_(self.bean2.prop1, 'testVal1')

        # The change should propagate to bean2
        self.bean1.prop1 = 'testVal3'
        eq_(self.bean1.prop1, 'testVal3')
        eq_(self.bean2.prop1, 'testVal3')

    def testTwoWayNoSync(self):
        bindProperty(self.bean1, 'prop1', self.bean2, 'prop1', True)

        # Nothing should've changed yet
        eq_(self.bean1.prop1, 'testVal1')
        eq_(self.bean2.prop1, 'testVal2')

        # The change should propagate to bean2
        self.bean1.prop1 = 'testVal3'
        eq_(self.bean1.prop1, 'testVal3')
        eq_(self.bean2.prop1, 'testVal3')

        # The change should propagate to bean1
        self.bean2.prop1 = 'testVal4'
        eq_(self.bean1.prop1, 'testVal4')
        eq_(self.bean2.prop1, 'testVal4')

    def testTwoWaySync(self):
        bindProperty(self.bean1, 'prop1', self.bean2, 'prop1', True, True)

        # Bean2.prop1 should have changed
        eq_(self.bean1.prop1, 'testVal1')
        eq_(self.bean2.prop1, 'testVal1')

        # The change should propagate to bean2
        self.bean1.prop1 = 'testVal3'
        eq_(self.bean1.prop1, 'testVal3')
        eq_(self.bean2.prop1, 'testVal3')

        # The change should propagate to bean1
        self.bean2.prop1 = 'testVal4'
        eq_(self.bean1.prop1, 'testVal4')
        eq_(self.bean2.prop1, 'testVal4')

    def testConverter(self):
        bindProperty(self.bean1, 'prop1', self.bean2, 'prop1',
                          converter=lambda v: 'xx%sxx' % v)

        # Nothing should've changed yet
        eq_(self.bean1.prop1, 'testVal1')
        eq_(self.bean2.prop1, 'testVal2')

        # The change should propagate to bean2 (with modifications)
        self.bean1.prop1 = 'testVal3'
        eq_(self.bean1.prop1, 'testVal3')
        eq_(self.bean2.prop1, 'xxtestVal3xx')

    def testDisconnect(self):
        adapter = bindProperty(self.bean1, 'prop1', self.bean2, 'prop1')

        # Nothing should've changed yet
        eq_(self.bean1.prop1, 'testVal1')
        eq_(self.bean2.prop1, 'testVal2')

        # The change should propagate to bean2
        self.bean1.prop1 = 'testVal3'
        eq_(self.bean1.prop1, 'testVal3')
        eq_(self.bean2.prop1, 'testVal3')

        # The change should propagate to bean1
        adapter.disconnect()
        self.bean2.prop1 = 'testVal4'
        eq_(self.bean1.prop1, 'testVal3')
        eq_(self.bean2.prop1, 'testVal4')
