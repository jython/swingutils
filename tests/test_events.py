from nose.tools import eq_

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
    eq_(event.firstIndex, 0)
    eq_(event.lastIndex, 0)


def testListSelectionEventNoArgs():
    def selectionListener():
        holder[0] = 1

    model = DefaultListModel()
    lst = JList(model)
    model.addElement(u'Test')
    holder = [None]
    addEventListener(lst, ListSelectionListener, 'valueChanged',
                     selectionListener)

    lst.setSelectionInterval(0, 0)
    eq_(holder, [1])


def testListSelectionEventVarargs():
    def selectionListener(*args):
        holder[0] = args

    model = DefaultListModel()
    lst = JList(model)
    model.addElement(u'Test')
    holder = [None]
    addEventListener(lst, ListSelectionListener, 'valueChanged',
                     selectionListener, 2)

    lst.setSelectionInterval(0, 0)
    eq_(holder[0], (2,))


def testListSelectionEventKwargs():
    def selectionListener(**kwargs):
        holder[0] = kwargs

    model = DefaultListModel()
    lst = JList(model)
    model.addElement(u'Test')
    holder = [None]
    addEventListener(lst, ListSelectionListener, 'valueChanged',
                     selectionListener, test=2)

    lst.setSelectionInterval(0, 0)
    eq_(holder[0], {'test': 2})
