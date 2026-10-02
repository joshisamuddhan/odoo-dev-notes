"""Decorators: timing, retry with exponential backoff, and a parameterised one."""
import functools
import logging
import time

_logger = logging.getLogger(__name__)


def timed(func):
    @functools.wraps(func)  # keep __name__, __doc__
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            _logger.info("%s took %.3fs", func.__name__, time.perf_counter() - start)
    return wrapper


def retry(times=3, exceptions=(Exception,), delay=1.0, backoff=2.0):
    """@retry(times=3, exceptions=(requests.RequestException,))
    Decorator WITH arguments = function returning a decorator returning a wrapper."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt == times:
                        raise
                    _logger.warning("%s failed (%s), retry %s/%s in %.1fs",
                                    func.__name__, exc, attempt, times - 1, wait)
                    time.sleep(wait)
                    wait *= backoff
        return wrapper
    return decorator
