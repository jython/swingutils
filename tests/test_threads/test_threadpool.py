from swingutils.threads.threadpool import TaskExecutor

executor = None


def setup():
    global executor
    executor = TaskExecutor()


def teardown():
    executor.shutdownNow()


def test_run_background():
    def task(x, y):
        return x + y

    future = executor.runBackground(task, 1, 2)
    assert future.result(1) == 3


def test_background_run():
    @executor.backgroundTask
    def task(x, y):
        return x + y

    future = task(1, 2)
    assert future.result(1) == 3
