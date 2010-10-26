from javax.swing.event import ListDataEvent, ListDataListener

from nose.tools import eq_

from swingutils.models.list import DelegateListModel
from swingutils.events import addEventListener


class TestListModel(object):
    addEvent = None
    removeEvent = None
    changeEvent = None

    def setup(self):
        self.model = DelegateListModel([])
        addEventListener(self.model, ListDataListener,
            'intervalAdded', self.intervalAdded)
        addEventListener(self.model, ListDataListener,
            'intervalRemoved', self.intervalRemoved)
        addEventListener(self.model, ListDataListener,
            'contentsChanged', self.contentsChanged)

    def intervalAdded(self, event):
        self.addEvent = event

    def intervalRemoved(self, event):
        self.removeEvent = event

    def contentsChanged(self, event):
        self.changeEvent = event

    def testDelItem(self):
        self.model.append('TEST')
        self.model.append('123')
        self.model.append(456)
        eq_(len(self.model), 3)

        del self.model[1]

        eq_(self.removeEvent.index0, 1)
        eq_(self.removeEvent.index1, 1)
        eq_(len(self.model), 2)

    def testDelSlice(self):
        self.model.append('TEST')
        self.model.append('123')
        self.model.append(456)
        self.model.append(789)
        eq_(len(self.model), 4)

        del self.model[1:3]

        eq_(self.removeEvent.index0, 1)
        eq_(self.removeEvent.index1, 2)
        eq_(len(self.model), 2)

    def testAppend(self):
        self.model.append(u'Test')

        eq_(self.addEvent.index0, 0)
        eq_(self.addEvent.index1, 0)
        eq_(self.addEvent.type, ListDataEvent.INTERVAL_ADDED)
        eq_(self.model[0], u'Test')

        self.model.append(345)

        eq_(self.addEvent.type, ListDataEvent.INTERVAL_ADDED)
        eq_(self.addEvent.index0, 1)
        eq_(self.addEvent.index1, 1)
        eq_(self.model[0], u'Test')
        eq_(self.model[1], 345)

    def testInsert(self):
        self.model.append(u'Test')
        self.model.append(u'Test3')
        eq_(self.model[0], u'Test')
        eq_(self.model[1], u'Test3')

        self.model.insert(1, 'Test2')

        eq_(self.addEvent.index0, 1)
        eq_(self.addEvent.index1, 1)
        eq_(len(self.model), 3)
        eq_(self.model[1], 'Test2')

        self.model.insert(0, 345)

        eq_(self.addEvent.index0, 0)
        eq_(self.addEvent.index1, 0)
        eq_(self.model[0], 345)
        eq_(len(self.model), 4)

    def testExtend(self):
        self.model.extend([u'Test', 'Test2', 678])

        eq_(self.addEvent.index0, 0)
        eq_(self.addEvent.index1, 2)
        eq_(self.model[0], u'Test')
        eq_(self.model[1], 'Test2')
        eq_(self.model[2], 678)

        self.model.extend([345, 7.0])

        eq_(self.addEvent.index0, 3)
        eq_(self.addEvent.index1, 4)
        eq_(self.model[3], 345)
        eq_(self.model[4], 7.0)

    def testSetSingle(self):
#        from nose.tools import set_trace; set_trace()
        self.model.append('abc')
        self.model[0] = '123'

        eq_(self.changeEvent.index0, 0)
        eq_(self.changeEvent.index1, 0)
        eq_(len(self.model), 1)
        eq_(self.model[0], '123')

    def testSetSlice(self):
        self.model.extend([u'Test', 'Test2', 678])
        self.model[2:4] = ['abc', 'xyz', 'foo']

        eq_(self.changeEvent.index0, 2)
        eq_(self.changeEvent.index1, 2)
        eq_(self.addEvent.index0, 3)
        eq_(self.addEvent.index1, 4)

        for i, val in enumerate([u'Test', 'Test2', 'abc', 'xyz', 'foo']):
            eq_(self.model[i], val)

    def testSetSliceReplace(self):
        self.model.extend([u'Test', 'Test2', 678])
        self.model[:] = ['abc', 'xyz']

        eq_(self.changeEvent.index0, 0)
        eq_(self.changeEvent.index1, 1)
        eq_(self.removeEvent.index0, 2)
        eq_(self.removeEvent.index1, 2)

        for i, val in enumerate(['abc', 'xyz']):
            eq_(self.model[i], val)

    def testDelegateReplace(self):
        self.model.delegate = [1, 2, 3]

        eq_(self.addEvent.index0, 0)
        eq_(self.addEvent.index1, 2)
        eq_(self.removeEvent, None)
        eq_(self.changeEvent, None)

        self.model.delegate = [7, 6, 1, 2, 4]
        eq_(self.addEvent.index0, 3)
        eq_(self.addEvent.index1, 4)
        eq_(self.removeEvent, None)
        eq_(self.changeEvent.index0, 0)
        eq_(self.changeEvent.index1, 2)

        del self.addEvent
        self.model.delegate = [4]
        eq_(self.addEvent, None)
        eq_(self.removeEvent.index0, 1)
        eq_(self.removeEvent.index1, 4)
        eq_(self.changeEvent.index0, 0)
        eq_(self.changeEvent.index1, 0)
        