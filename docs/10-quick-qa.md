# Quick Q&A — concepts you may be asked while building (generic Odoo, 2 sentences each)

**`_inherit` vs `_inherits`?** `_inherit` extends a model in place (same table) or copies it into a new `_name`; `_inherits` delegates: a new model holds a many2one to the parent and exposes its fields (separate tables).
**Compute vs onchange vs related?** Compute derives a value from dependencies (works on API/import too); onchange is UI-only suggestion; related is a compute shortcut that follows a path.
**`store=True` trade-offs?** Enables search/group/index but costs recompute time and disk; every field in `@api.depends` triggers recompute.
**ACL vs record rule?** ACL = model-level CRUD per group; record rule = row-level domain filter. Both must pass; rules never grant access that ACL denies.
**What does `sudo()` do?** Runs as superuser bypassing ACLs/rules — risky; scope it to the smallest operation, never return sudo'd data to the user blindly.
**What happens on `write()`?** ACL+rules check → `write` overrides (MRO) → values converted/cached → SQL UPDATE → recompute of dependent stored fields → constraints (`@api.constrains`) run → tracking/chatter messages.
**`search` vs `filtered`?** `search` hits the DB with a domain; `filtered` runs a Python lambda in memory on an existing recordset.
**`mapped` vs list comprehension?** `mapped("a.b")` follows relations with prefetch and returns a recordset/list; shorter and avoids N+1.
**N+1 problem?** One query per record inside a loop; fix with batched `search` on `in`, `read_group`, prefetch, or stored computes.
**`read_group`?** Server-side aggregation (GROUP BY) returning sums/counts per group — avoids Python loops. (v17+: `_read_group` tuples.)
**`@api.model` vs `@api.model_create_multi`?** First: method not tied to records (`self` empty). Second: `create` receives a list of dicts (batch create).
**`ondelete` options?** `set null` (default for optional m2o), `restrict` (block delete), `cascade` (delete children).
**Transient vs Abstract vs normal model?** Transient = temp wizard data (auto-vacuumed); Abstract = mixin with no table; normal = persistent.
**How do you add a field to a core view?** Inherit the view, XPath/`position` into the right spot. Never edit core files.
**`noupdate="1"`?** Data records are created on install but not overwritten on later `-u` (use for user-editable data like templates/sequences).
**Multi-company?** `company_id` on records, rule `[('company_id','in',company_ids)]`, `check_company`, switch via company menu; `allowed_company_ids` in context.
**Cron?** `ir.cron` runs a method as a user on schedule via cron workers; keep idempotent, batch, commit progress, handle failures per record.
**Report engine?** QWeb template → HTML → wkhtmltopdf → PDF; `ir.actions.report` binds it to a model.
**How does Odoo load modules?** Dependency graph from `depends` → install order → `data` files in manifest order → registry built; models merged via MRO.
**Delete vs archive?** `active=False` hides without breaking references; prefer archive.
**Access from external system?** XML-RPC/JSON-RPC with API key, or custom REST controller.
**Why API keys?** Revocable, scoped credentials instead of passwords; work with 2FA accounts.
**Idempotent HTTP methods?** GET, PUT, DELETE (and HEAD/OPTIONS); POST is not — design retry-safe POSTs with external ids.
**401 vs 403?** 401 = not authenticated; 403 = authenticated but forbidden.
**Webhooks vs polling?** Push vs pull; webhooks need verification (HMAC), fast ack, retries and dedupe.
**How do you improve a slow report?** Measure first (`--log-sql`, `EXPLAIN ANALYZE`), kill N+1, SQL aggregation, index, store computes, cache, async generation.
**Deploying on Odoo.sh vs on-prem?** Odoo.sh = Git branches (prod/staging/dev), automatic builds/backups, no root; on-prem = full control (nginx, workers, PG tuning) but you operate it.
**Upgrade strategy?** Clone prod → upgrade scripts (OpenUpgrade/standard) per version hop → fix custom modules → validate totals → UAT → cutover.
**Testing in Odoo?** `TransactionCase` (rolls back), `HttpCase` (controllers/tours), `Form` for UI-like onchange tests, tags `post_install`.
**Security basics (OWASP)?** Access control (ACL/rules), injection (params/ORM), XSS (QWeb escaping), CSRF (tokens), auth (strong passwords/2FA/session timeout), misconfig (headers, debug off, `list_db=False`), file upload validation.

## Questions you can ask them
How is the codebase structured for multiple clients? How are upgrades handled? Is there CI/code review? What does the first month look like? How is production support organised?
