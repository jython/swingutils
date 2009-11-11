from nose.tools import eq_

from javax.swing import JList, DefaultListModel

from swingutils.events import addEventListener


def testListSelectionEvent():
    def selectionListener(event, eventHolder):
        eventHolder[0] = event

    model = DefaultListModel()
    lst = JList(model)
    model.addElement(u'Test')
    eventHolder = [None]
    addEventListener(lst, 'valueChanged', selectionListener, eventHolder)

    lst.setSelectionInterval(0, 0)
    event = eventHolder[0]
    eq_(event.firstIndex, 0)
    eq_(event.lastIndex, 0)
