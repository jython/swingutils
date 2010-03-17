# coding: utf-8
from nose.tools import eq_

from swingutils.beans import JavaBeanSupport, AutoChangeNotifier, MirrorObject
from swingutils.events import addPropertyListener


def testPropertyChange():
    class DummyBean(JavaBeanSupport):
        def testFire(self):
            self.firePropertyChange(u'testProperty', None, u'newVal')

    def listener(event, listenerOk):
        listenerOk[0] = True
        eq_(event.oldValue, None)
        eq_(event.newValue, 'newVal')

    listenerOk = [False]
    bean = DummyBean()
    wrapper = addPropertyListener(bean, u'testProperty', listener, listenerOk)
    bean.testFire()
    eq_(listenerOk[0], True)

    listenerOk = [False]
    bean.removePropertyChangeListener(u'testProperty', wrapper)
    bean.testFire()
    eq_(listenerOk[0], False)


def testAllPropertyChange():
    class DummyBean(JavaBeanSupport):
        def testFire(self):
            self.firePropertyChange(u'testProperty', None, u'newVal')

    def listener(event, listenerOk):
        listenerOk[0] = True
        eq_(event.propertyName, u'testProperty')
        eq_(event.oldValue, None)
        eq_(event.newValue, 'newVal')

    listenerOk = [False]
    bean = DummyBean()
    wrapper = addPropertyListener(bean, None, listener, listenerOk)
    bean.testFire()
    eq_(listenerOk[0], True)

    listenerOk = [False]
    bean.removePropertyChangeListener(wrapper)
    bean.testFire()
    eq_(listenerOk[0], False)


def testAutoProperty():
    class DummyBean(JavaBeanSupport, AutoChangeNotifier):
        prop = 'test1'

    def listener(event, listenerOk):
        listenerOk[0] = True
        eq_(event.oldValue, 'test1')
        eq_(event.newValue, 'test2')

    listenerOk = [False]
    bean = DummyBean()
    wrapper = addPropertyListener(bean, u'prop', listener, listenerOk)
    bean.prop = 'test2'
    eq_(listenerOk[0], True)

    listenerOk = [False]
    bean.removePropertyChangeListener(u'prop', wrapper)
    bean.prop = 'test3'
    eq_(listenerOk[0], False)


class DummyBean1(object):
    prop1 = 'foo'
    prop2 = 'bar'


class DummyBean2(object):
    prop2 = 'abc'
    prop3 = 'xyz'


class TestMirrorObject(object):
    def setup(self):
        self.mirror = MirrorObject(DummyBean1())
        self.propertyValue1 = None
        self.propertyValue2 = None
        self.changes = []
        addPropertyListener(self.mirror, 'prop1', self.prop1listener)
        addPropertyListener(self.mirror, 'prop2', self.prop2listener)
        addPropertyListener(self.mirror, 'prop3', self.prop3listener)
        addPropertyListener(self.mirror, None, self.allListener)

    def prop1listener(self, event):
        self.propertyValue1 = event.newValue

    def prop2listener(self, event):
        self.propertyValue2 = event.newValue

    def prop3listener(self, event):
        self.propertyValue3 = event.newValue

    def allListener(self, event):
        self.changes.append((event.propertyName, event.newValue))

    def testDelegateProperties(self):
        eq_(self.mirror.prop1, 'foo')
        eq_(self.mirror.prop2, 'bar')

    def testPropertyChange(self):
        self.mirror.prop2 = 'bleh'
        eq_(self.propertyValue2, 'bleh')
        eq_(self.changes, [('prop2', 'bleh')])

    def testDelegateChange(self):
        self.mirror._delegate = DummyBean2()
        eq_(self.propertyValue1, None)
        eq_(self.propertyValue2, 'abc')
        eq_(self.propertyValue3, 'xyz')
