from javax.swing.event import ListDataEvent, ListDataListener

from nose.tools import eq_

from swingutils.models.list import DelegateListModel
from swingutils.events import addEventListener


class TestListModel(object):
    def setup(self):
        self.model = DelegateListModel([])

    @staticmethod
    def contentsChanged(event, result):
        result[0] = event

    @staticmethod
    def intervalAdded(event, result):
        result[0] = event

    @staticmethod
    def intervalRemoved(event, result):
        result[0] = event

    def testDelItem(self):
        result = [None]
        addEventListener(self.model, ListDataListener,
            'intervalRemoved', self.intervalRemoved, result)

        self.model.append('TEST')
        self.model.append('123')
        self.model.append(456)
        eq_(len(self.model), 3)

        del self.model[1]

        event = result[0]
        assert event
        eq_(event.type, ListDataEvent.INTERVAL_REMOVED)
        eq_(event.index0, 1)
        eq_(event.index1, 1)
        eq_(len(self.model), 2)

    def testDelSlice(self):
        result = [None]
        addEventListener(self.model, ListDataListener,
            'intervalRemoved', self.intervalRemoved, result)

        self.model.append('TEST')
        self.model.append('123')
        self.model.append(456)
        self.model.append(789)
        eq_(len(self.model), 4)

        del self.model[1:3]
        event = result[0]
        assert event
        eq_(event.type, ListDataEvent.INTERVAL_REMOVED)
        eq_(event.index0, 1)
        eq_(event.index1, 2)
        eq_(len(self.model), 2)

    def testAppend(self):
        result = [None]
        addEventListener(self.model, ListDataListener,
                                 'intervalAdded', self.intervalAdded, result)

        self.model.append(u'Test')

        event = result[0]
        assert event
        eq_(event.index0, 0)
        eq_(event.index1, 0)
        eq_(event.type, ListDataEvent.INTERVAL_ADDED)
        eq_(self.model[0], u'Test')

        self.model.append(345)

        event = result[0]
        assert event
        eq_(event.type, ListDataEvent.INTERVAL_ADDED)
        eq_(event.index0, 1)
        eq_(event.index1, 1)
        eq_(self.model[0], u'Test')
        eq_(self.model[1], 345)

    def testInsert(self):
        result = [None]
        self.model.append(u'Test')
        self.model.append(u'Test3')
        eq_(self.model[0], u'Test')
        eq_(self.model[1], u'Test3')

        addEventListener(self.model, ListDataListener,
                                 'intervalAdded', self.intervalAdded, result)

        self.model.insert(1, 'Test2')

        event = result[0]
        assert event
        eq_(event.index0, 1)
        eq_(event.index1, 1)
        eq_(event.type, ListDataEvent.INTERVAL_ADDED)
        eq_(len(self.model), 3)
        eq_(self.model[1], 'Test2')

        self.model.insert(0, 345)

        event = result[0]
        assert event
        eq_(event.type, ListDataEvent.INTERVAL_ADDED)
        eq_(event.index0, 0)
        eq_(event.index1, 0)
        eq_(self.model[0], 345)
        eq_(len(self.model), 4)

    def testExtend(self):
        result = [None]
        addEventListener(self.model, ListDataListener,
                                 'intervalAdded', self.intervalAdded, result)

        self.model.extend([u'Test', 'Test2', 678])

        event = result[0]
        assert event
        eq_(event.index0, 0)
        eq_(event.index1, 2)
        eq_(event.type, ListDataEvent.INTERVAL_ADDED)
        eq_(self.model[0], u'Test')
        eq_(self.model[1], 'Test2')
        eq_(self.model[2], 678)

        self.model.extend([345, 7.0])

        event = result[0]
        assert event
        eq_(event.type, ListDataEvent.INTERVAL_ADDED)
        eq_(event.index0, 3)
        eq_(event.index1, 4)
        eq_(self.model[3], 345)
        eq_(self.model[4], 7.0)

    def testSetSlice(self):
        result1 = [None]
        result2 = [None]
        self.model.extend([u'Test', 'Test2', 678])

        addEventListener(self.model, ListDataListener,
            'contentsChanged', self.contentsChanged, result1)
        addEventListener(self.model, ListDataListener,
            'intervalAdded', self.intervalAdded, result2)

        self.model[2:4] = ['abc', 'xyz', 'foo']

        event = result1[0]
        assert event
        eq_(event.type, ListDataEvent.CONTENTS_CHANGED)
        eq_(event.index0, 2)
        eq_(event.index1, 2)

        event = result2[0]
        assert event
        eq_(event.type, ListDataEvent.INTERVAL_ADDED)
        eq_(event.index0, 3)
        eq_(event.index1, 4)

        for i, val in enumerate([u'Test', 'Test2', 'abc', 'xyz', 'foo']):
            eq_(self.model[i], val)

    def testSetSliceReplace(self):
        result1 = [None]
        result2 = [None]
        self.model.extend([u'Test', 'Test2', 678])

        addEventListener(self.model, ListDataListener,
            'contentsChanged', self.contentsChanged, result1)
        addEventListener(self.model, ListDataListener,
            'intervalRemoved', self.intervalRemoved, result2)

        self.model[:] = ['abc', 'xyz']

        event = result1[0]
        assert event
        eq_(event.type, ListDataEvent.CONTENTS_CHANGED)
        eq_(event.index0, 0)
        eq_(event.index1, 1)

        event = result2[0]
        assert event
        eq_(event.type, ListDataEvent.INTERVAL_REMOVED)
        eq_(event.index0, 2)
        eq_(event.index1, 2)

        for i, val in enumerate(['abc', 'xyz']):
            eq_(self.model[i], val)
