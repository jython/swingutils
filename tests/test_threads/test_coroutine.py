from concurrent.futures import Future

from swingutils.threads.coroutine import swingCoroutine, returnValue, setDefaultCoroutineExceptionHandler
from threading import Event


def add(x, y):
    future = Future()
    future.set_result(x + y)
    return future


def test_swing_coroutine():
    @swingCoroutine
    def inner():
        res = yield add(1, 2)
        res = yield add(res, 3)
        returnValue(res)

    future = inner()
    assert future.result(1) == 6


def test_swing_coroutine_exception():
    class TestError(Exception):
        pass

    def excepthook(exc_type, exc_value, tb):
        excepthook_event.set()

    @swingCoroutine
    def raiseException():
        yield add(1, 2)
        raise TestError

    excepthook_event = Event()
    setDefaultCoroutineExceptionHandler(excepthook)
    try:
        future = raiseException()
        exc = future.exception(1)
        assert excepthook_event.wait(1)
    finally:
        setDefaultCoroutineExceptionHandler(None)

    assert isinstance(exc, TestError)
