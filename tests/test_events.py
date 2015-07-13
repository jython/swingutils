from javax.swing import JList, DefaultListModel
from javax.swing.event import ListSelectionListener

from swingutils.events import addEventListener


def testListSelectionEvent():
    def selectionListener(event):
        eventHolder[0] = event

    model = DefaultListModel()
    lst = JList(model)
    model.addElement(u'Test')
    eventHolder = [None]
    addEventListener(lst, ListSelectionListener, 'valueChanged',
                     selectionListener)

    lst.setSelectionInterval(0, 0)
    event = eventHolder[0]
    assert event.firstIndex == 0
    assert event.lastIndex == 0


def testListSelectionEventVarargs():
    def selectionListener(*args):
        _event, holder[0] = args

    model = DefaultListModel()
    lst = JList(model)
    model.addElement(u'Test')
    holder = [None]
    addEventListener(lst, ListSelectionListener, 'valueChanged',
                     selectionListener, 2)

    lst.setSelectionInterval(0, 0)
    assert holder[0] == 2


def testListSelectionEventKwargs():
    def selectionListener(event, **kwargs):
        holder[0] = kwargs

    model = DefaultListModel()
    lst = JList(model)
    model.addElement(u'Test')
    holder = [None]
    addEventListener(lst, ListSelectionListener, 'valueChanged',
                     selectionListener, test=2)

    lst.setSelectionInterval(0, 0)
    assert holder[0] == {'test': 2}


def testBuiltinListener():
    model = DefaultListModel()
    lst = JList(model)
    model.addElement(u'Test')
    events = []
    addEventListener(lst, ListSelectionListener, 'valueChanged',
                     events.append)

    lst.setSelectionInterval(0, 0)
    assert len(events) == 1
    assert events[0].firstIndex == 0
    assert events[0].lastIndex == 0
