from nose.tools import eq_, raises

from swingutils.beans import AutoChangeNotifier
from swingutils.binding import connect


class TestBase(object):
    def setup(self):
        self.bean1 = AutoChangeNotifier()
        self.bean2 = AutoChangeNotifier()
        self.bean1.prop1 = 'testVal1'
        self.bean2.prop1 = 'testVal2'

    def testOneWayNoSync(self):
        connect(self.bean1, 'prop1', self.bean2, 'prop1')

        # Nothing should've changed yet
        eq_(self.bean1.prop1, 'testVal1')
        eq_(self.bean2.prop1, 'testVal2')

        # The change should propagate to bean2
        self.bean1.prop1 = 'testVal3'
        eq_(self.bean1.prop1, 'testVal3')
        eq_(self.bean2.prop1, 'testVal3')

    def testOneWaySync(self):
        connect(self.bean1, 'prop1', self.bean2, 'prop1', syncNow=True)

        # Bean2.prop1 should have changed
        eq_(self.bean1.prop1, 'testVal1')
        eq_(self.bean2.prop1, 'testVal1')

        # The change should propagate to bean2
        self.bean1.prop1 = 'testVal3'
        eq_(self.bean1.prop1, 'testVal3')
        eq_(self.bean2.prop1, 'testVal3')

    def testTwoWayNoSync(self):
        connect(self.bean1, 'prop1', self.bean2, 'prop1', True)

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
        connect(self.bean1, 'prop1', self.bean2, 'prop1', True, True)

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
        connect(self.bean1, 'prop1', self.bean2, 'prop1',
                converter=lambda v: 'xx%sxx' % v)

        # Nothing should've changed yet
        eq_(self.bean1.prop1, 'testVal1')
        eq_(self.bean2.prop1, 'testVal2')

        # The change should propagate to bean2 (with modifications)
        self.bean1.prop1 = 'testVal3'
        eq_(self.bean1.prop1, 'testVal3')
        eq_(self.bean2.prop1, 'xxtestVal3xx')

    @raises(AssertionError)
    def testTwowayConverter(self):
        connect(self.bean1, 'prop1', self.bean2, 'prop1', True,
                converter=lambda v: 'xx%sxx' % v)

    def testDisconnect(self):
        adapter = connect(self.bean1, 'prop1', self.bean2, 'prop1')

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
