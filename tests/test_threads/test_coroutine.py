from concurrent.futures import Future

from nose.tools import eq_

from swingutils.threads.coroutine import swingCoroutine, returnValue


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
    eq_(future.result(1), 6)


def test_swing_coroutine_no_generator():
    """
    Tests that an @swing_coroutine decorated function returns a future with
    the return value preset if it's not a generator.
    """

    @swingCoroutine
    def inner(x, y):
        return x + y

    future = inner(1, 2)
    eq_(future.result(0), 3)


def test_swing_coroutine_exception():
    class TestError(Exception):
        pass

    @swingCoroutine
    def raiseException():
        yield add(1, 2)
        raise TestError

    future = raiseException()
    exc = future.exception(1)
    assert isinstance(exc, TestError)
