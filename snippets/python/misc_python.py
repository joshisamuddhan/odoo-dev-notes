"""Small things interviewers like: context manager, LRU cache, monthly aggregation, gotchas."""
from collections import OrderedDict, defaultdict
from contextlib import contextmanager


@contextmanager
def managed(resource_factory):
    res = resource_factory()
    try:
        yield res
    finally:
        res.close()  # always runs, even on exception


class LRU:
    def __init__(self, size):
        self.size, self.data = size, OrderedDict()

    def get(self, k, default=None):
        if k not in self.data:
            return default
        self.data.move_to_end(k)
        return self.data[k]

    def put(self, k, v):
        self.data[k] = v
        self.data.move_to_end(k)
        if len(self.data) > self.size:
            self.data.popitem(last=False)


def monthly_totals(rows):
    out = defaultdict(lambda: {"insertions": 0, "deletions": 0})
    for r in rows:
        m = r["date"][:7]  # "2026-06"
        out[m]["insertions"] += r["insertions"]
        out[m]["deletions"] += r["deletions"]
    return dict(out)


def bad_default(x, acc=[]):   # GOTCHA: default list is created ONCE and shared
    acc.append(x)
    return acc


def good_default(x, acc=None):
    acc = [] if acc is None else acc
    acc.append(x)
    return acc
