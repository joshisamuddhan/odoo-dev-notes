"""Batch helpers: chunking, flatten, dedupe-keep-order, safe parsing."""
from itertools import islice


def chunks(iterable, size):
    """Lazily yield lists of `size` items. In Odoo: odoo.tools.split_every(size, ids)."""
    it = iter(iterable)
    while batch := list(islice(it, size)):
        yield batch


def flatten(items):
    for x in items:
        if isinstance(x, (list, tuple)):
            yield from flatten(x)
        else:
            yield x


def dedupe(seq):
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]  # set() alone loses order


def as_list(value):
    """API sometimes returns object, list or null: normalise to list."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]

# Odoo cron over many records, committing progress:
#   ids = self.search([...]).ids
#   for batch in split_every(500, ids):
#       self.browse(batch)._process()
#       self.env.cr.commit()          # only in cron/scripts, never in normal request code
#       self.env.invalidate_all()
