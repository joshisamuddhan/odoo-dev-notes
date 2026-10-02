"""Run: python3 selftest.py  -> quick sanity check of all helpers."""
from batching import as_list, chunks, dedupe, flatten
from decorators import retry
from graph_cycle import find_cycle, topo_order
from hmac_webhook import verify_hmac_b64, verify_hmac_hex
from misc_python import LRU, monthly_totals
from token_bucket import TokenBucket
import hashlib, hmac, base64

assert list(chunks(range(5), 2)) == [[0, 1], [2, 3], [4]]
assert list(flatten([1, [2, [3, 4], 5], 6])) == [1, 2, 3, 4, 5, 6]
assert dedupe([3, 1, 3, 2, 1]) == [3, 1, 2]
assert as_list(None) == [] and as_list({"a": 1}) == [{"a": 1}]
g = {"line": ["order", "product"], "order": ["partner"], "partner": [], "product": []}
assert topo_order(g).index("partner") < topo_order(g).index("order")
assert find_cycle({"a": ["b"], "b": ["a"]}) == ["a", "b", "a"]
calls = []
@retry(times=3, delay=0, exceptions=(ValueError,))
def flaky():
    calls.append(1)
    if len(calls) < 3:
        raise ValueError
    return "ok"
assert flaky() == "ok" and len(calls) == 3
body, secret = b'{"a":1}', "s3"
assert verify_hmac_hex(body, secret, hmac.new(b"s3", body, hashlib.sha256).hexdigest())
assert verify_hmac_b64(body, secret, base64.b64encode(hmac.new(b"s3", body, hashlib.sha256).digest()).decode())
c = LRU(2); c.put(1, 1); c.put(2, 2); c.get(1); c.put(3, 3)
assert c.get(2) is None and c.get(1) == 1
assert monthly_totals([{"date": "2026-06-08", "insertions": 5, "deletions": 1}])["2026-06"]["insertions"] == 5
TokenBucket(100).acquire()
print("all python snippets OK")
