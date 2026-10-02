# Python essentials (quick answers + patterns)

Runnable examples with self-test: `../snippets/python/` (run `python3 selftest.py`).

## Concepts (one-liners)
- **Decorator**: function that takes a function and returns a new one, adding behaviour. Use `functools.wraps`. With args → 3 levels. (`decorators.py`)
- **list/tuple/set/dict**: ordered mutable / ordered immutable / unordered unique / key-value (ordered by insertion). Set & dict lookups O(1).
- **`is` vs `==`**: identity vs equality (`None` checks use `is`).
- **`*args/**kwargs`**: variable positional / keyword args; unpack with `f(*lst, **d)`.
- **Mutable default argument** gotcha → use `None` sentinel. (`misc_python.py`)
- **Shallow vs deep copy**: `copy.copy` shares nested objects; `deepcopy` clones recursively.
- **List comprehension vs generator**: eager list in memory vs lazy one-at-a-time (`(x for x in ...)`); use generators for big data.
- **Generators** `yield` — lazy streams, batching (`batching.py`).
- **Context manager** `with`: `__enter__/__exit__` or `@contextmanager` — guaranteed cleanup.
- **@staticmethod / @classmethod / instance**: no self / receives cls / receives self. Odoo `@api.model` ≈ method on the model not records.
- **MRO**: C3 linearisation; `Class.__mro__`; Odoo `_inherit` builds the class from multiple bases → `super()` chain order = module load order (later module overrides earlier).
- **GIL**: one thread runs Python bytecode at a time → threads help I/O-bound (API calls), not CPU-bound → use `multiprocessing`/workers.
- **`__slots__`, dataclasses, `typing`**, f-strings, walrus `:=`, `enumerate/zip/any/all/sorted(key=)`, `collections.defaultdict/Counter/deque/OrderedDict`, `itertools.groupby/islice/chain`, `functools.lru_cache/partial/reduce`.
- **Exceptions**: `try/except/else/finally`, `raise ... from e`, custom exception classes; catch narrow exceptions.
- **Immutability/hashability**: dict keys must be hashable.
- **Time complexity**: `x in list` O(n) vs `x in set` O(1); sort O(n log n).
- **Virtualenv/pip**: `python3 -m venv venv`, `pip install -r requirements.txt`, `pip freeze`.
- **PEP8/flake8/black/ruff** (Odoo 18 ships `ruff.toml`).
- **Logging** not print: `_logger = logging.getLogger(__name__)`.
- **Unit tests**: `unittest`/`pytest`; Odoo `TransactionCase`, `Form` helper (`from odoo.tests import Form`).

## Frequent live-coding tasks (solutions in snippets)
| Task | File |
|---|---|
| retry with exponential backoff | `decorators.py` |
| timing decorator | `decorators.py` |
| paginate API until empty | `paginated_fetch.py` |
| HMAC webhook check | `hmac_webhook.py` |
| token-bucket limiter | `token_bucket.py` |
| chunk/batch generator, flatten, dedupe keep order, normalise api value | `batching.py` |
| cycle detection / topological sort | `graph_cycle.py` |
| LRU cache, monthly aggregation | `misc_python.py` |
| parameterised UPSERT | `upsert_sql.py` |
| palindrome / reverse | `s[::-1]`, `s == s[::-1]` |
| FizzBuzz / two-sum / anagram / count words | `Counter(s.split())`; two-sum with dict: `seen[target-x]` |

## Mini-recipes
```python
from collections import Counter, defaultdict
Counter("a b a".split()).most_common(1)           # [('a', 2)]
groups = defaultdict(list); [groups[r["k"]].append(r) for r in rows]
sorted(rows, key=lambda r: (r["state"], -r["amount"]))
sum(x["amount"] for x in rows if x["ok"])
{k: v for k, v in d.items() if v}
json.dumps(obj, default=str)    # dates/decimals
datetime.strptime("2026-10-03", "%Y-%m-%d").date()
```
