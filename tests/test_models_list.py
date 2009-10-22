from swingutils.models.list import ListModel

from javax.swing.event import ListDataEvent

from nose.tools import eq_


model = None




def makeEventListener(func, *args):
    def wrapper(event):
        func(event, *args)
    return wrapper

class TestListModel(object):
    def setup(self):
        global model
        model = ListModel()

    def testDelItem(self):
        def intervalRemoved(event, result):
            result[0] = event

        result = [None]
        model.intervalRemoved = makeEventListener(intervalRemoved, result)

        model.append('TEST')
        model.append('123')
        model.append(456)
        eq_(len(model), 3)

        del model[1]
        event = result[0]
        assert event
        eq_(event.type, ListDataEvent.INTERVAL_REMOVED)
        eq_(event.index0, 1)
        eq_(event.index1, 1)
        eq_(len(model), 2)

    def testDelSlice(self):
        def intervalRemoved(event, result):
            result[0] = event

        result = [None]
        model.intervalRemoved = makeEventListener(intervalRemoved, result)
        
        model.append('TEST')
        model.append('123')
        model.append(456)
        model.append(789)
        eq_(len(model), 4)

        del model[1:3]
        event = result[0]
        assert event
        eq_(event.type, ListDataEvent.INTERVAL_REMOVED)
        eq_(event.index0, 1)
        eq_(event.index1, 2)
        eq_(len(model), 2)

    def testAppend(self):
        def intervalAdded(event, result):
            result[0] = event

        result = [None]
        model.intervalAdded = makeEventListener(intervalAdded, result)

        model.append(u'Test')
        event = result[0]
        assert event
        eq_(event.index0, 0)
        eq_(event.index1, 0)
        eq_(event.type, ListDataEvent.INTERVAL_ADDED)
        eq_(model[0], u'Test')

        model.append(345)
        event = result[0]
        assert event
        eq_(event.type, ListDataEvent.INTERVAL_ADDED)
        eq_(event.index0, 1)
        eq_(event.index1, 1)
        eq_(model[0], u'Test')
        eq_(model[1], 345)

    def testInsert(self):
        def intervalAdded(event, result):
            result[0] = event

        result = [None]
        model.append(u'Test')
        model.append(u'Test3')
        eq_(model[0], u'Test')
        eq_(model[1], u'Test3')

        model.intervalAdded = makeEventListener(intervalAdded, result)
        model.insert(1, 'Test2')
        event = result[0]
        assert event
        eq_(event.index0, 1)
        eq_(event.index1, 1)
        eq_(event.type, ListDataEvent.INTERVAL_ADDED)
        eq_(len(model), 3)
        eq_(model[1], 'Test2')

        model.insert(0, 345)
        event = result[0]
        assert event
        eq_(event.type, ListDataEvent.INTERVAL_ADDED)
        eq_(event.index0, 0)
        eq_(event.index1, 0)
        eq_(model[0], 345)
        eq_(len(model), 4)

    def testExtend(self):
        def intervalAdded(event, result):
            result[0] = event

        result = [None]
        model.intervalAdded = makeEventListener(intervalAdded, result)
        model.extend([u'Test', 'Test2', 678])
        event = result[0]
        assert event
        eq_(event.index0, 0)
        eq_(event.index1, 2)
        eq_(event.type, ListDataEvent.INTERVAL_ADDED)
        eq_(model[0], u'Test')
        eq_(model[1], 'Test2')
        eq_(model[2], 678)

        model.extend([345, 7.0])
        event = result[0]
        assert event
        eq_(event.type, ListDataEvent.INTERVAL_ADDED)
        eq_(event.index0, 3)
        eq_(event.index1, 4)
        eq_(model[3], 345)
        eq_(model[4], 7.0)
