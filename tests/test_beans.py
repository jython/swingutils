# coding: utf-8
from nose.tools import eq_

from swingutils.beans import JavaBeanSupport, AutoChangeNotifier


def testPropertyChange():
    class DummyBean(JavaBeanSupport):
        def testFire(self):
            self._firePropertyChange(u'testProperty', None, u'newVal')

    def listener(old, new, listenerOk):
        listenerOk[0] = True
        eq_(old, None)
        eq_(new, 'newVal')

    listenerOk = [False]
    bean = DummyBean()
    wrapper = bean.addPropertyListener(listener, u'testProperty', listenerOk)
    bean.testFire()
    eq_(listenerOk[0], True)

    listenerOk = [False]
    bean.removePropertyListener(wrapper, u'testProperty')
    bean.testFire()
    eq_(listenerOk[0], False)


def testAllPropertyChange():
    class DummyBean(JavaBeanSupport):
        def testFire(self):
            self._firePropertyChange(u'testProperty', None, u'newVal')

    def listener(property, old, new, listenerOk):
        listenerOk[0] = True
        eq_(property, u'testProperty')
        eq_(old, None)
        eq_(new, 'newVal')

    listenerOk = [False]
    bean = DummyBean()
    wrapper = bean.addPropertyListener(listener, None, listenerOk)
    bean.testFire()
    eq_(listenerOk[0], True)

    listenerOk = [False]
    bean.removePropertyListener(wrapper)
    bean.testFire()
    eq_(listenerOk[0], False)


def testAutoProperty():
    class DummyBean(AutoChangeNotifier):
        prop = 'test1'

    def listener(old, new, listenerOk):
        listenerOk[0] = True
        eq_(old, 'test1')
        eq_(new, 'test2')

    listenerOk = [False]
    bean = DummyBean()
    wrapper = bean.addPropertyListener(listener, u'prop', listenerOk)
    bean.prop = 'test2'
    eq_(listenerOk[0], True)

    listenerOk = [False]
    bean.removePropertyListener(wrapper, u'prop')
    bean.prop = 'test3'
    eq_(listenerOk[0], False)
