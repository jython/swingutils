# coding: utf-8
from nose.tools import eq_

from swingutils.beans import JavaBeanSupport, AutoChangeNotifier
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
    class DummyBean(AutoChangeNotifier):
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
