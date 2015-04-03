from threading import Event

from swingutils.threads.swing import callSwing, swingCall, swingRun, runSwing


def test_call_swing():
    assert callSwing(list, (1, 2)) == [1, 2]


def test_swing_call():
    assert swingCall(list)((1, 2)) == [1, 2]


def test_run_swing():
    runSwing(Event().wait, 1)


def test_swing_run():
    swingRun(Event().wait)(1)
