"""Client-side rate limiter: allow `rate` calls per second."""
import threading
import time


class TokenBucket:
    def __init__(self, rate, capacity=None):
        self.rate, self.capacity = rate, capacity or rate
        self.tokens, self.updated = self.capacity, time.monotonic()
        self.lock = threading.Lock()

    def acquire(self):
        while True:
            with self.lock:
                now = time.monotonic()
                self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
                self.updated = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
                wait = (1 - self.tokens) / self.rate
            time.sleep(wait)
