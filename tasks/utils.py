from tornado.concurrent import TracebackFuture
from tornado.ioloop import IOLoop


def async_task(task, *args, **kwargs):
    """
    Async task factory. This method adapts Celery behavior to work within a 
    Tornado application.
    """
    def _on_result(result, future):
        # If the result is ready, update the future. Otherwise recheck on the next
        # loop.
        if result.ready():
            future.set_result(result.result)
        else:
            IOLoop.instance().add_callback(_on_result, result, future)

    future = TracebackFuture()
    result = task.apply_async(*args, **kwargs)
    IOLoop.instance().add_callback(_on_result, result, future)

    # Return future once it has resolved.
    return future
