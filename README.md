# Odoo Dev Notes & Starter Kit

Personal, generic reference for timed practical Odoo tasks. **No client code or credentials** — the demo module is a made-up library app.
Tested on this machine against Odoo 18 community: module installs from scratch, 5 unit tests pass, REST API verified with curl.

## Start here (on test day)
1. `docs/01-task-day-playbook.md` — time plan, questions to ask, build order, final checklist
2. Find the Odoo version → `docs/03-version-differences.md` (top section)
3. Copy the skeleton: `snippets/library_demo/` (rename the module, models, xml ids)
4. Look things up in `docs/02-odoo-cheatsheet.md`; errors in `docs/08-troubleshooting.md`

## Index
| File | What |
|---|---|
| `docs/01-task-day-playbook.md` | Timeline, questions for the interviewer, README template |
| `docs/02-odoo-cheatsheet.md` | Models, fields, ORM, views, security, wizard, reports, controllers |
| `docs/03-version-differences.md` | v14→v19 syntax changes (verified against source) |
| `docs/04-commands.md` | odoo-bin, psql, git, linux, debugging commands |
| `docs/05-api-and-integrations.md` | REST design, status codes, XML-RPC, sync patterns, curl |
| `docs/06-python-essentials.md` | Python concepts + live-coding map |
| `docs/07-sql-postgres.md` | Queries, EXPLAIN, indexes, safety |
| `docs/08-troubleshooting.md` | Error → cause → fix table |
| `docs/09-security-performance-checklist.md` | Final review checklist |
| `docs/10-quick-qa.md` | Short answers to common Odoo questions |
| `docs/11-practice-tasks.md` | Timed mock tasks + rubric |
| `snippets/library_demo/` | Complete Odoo 18 module: models, views, security, wizard, cron, mail, report, REST API, tests |
| `snippets/python/` | retry/timing decorators, pagination, HMAC, XML-RPC, rate limiter, graph cycle… (`python3 selftest.py`) |

## Use the skeleton
```bash
cp -r snippets/library_demo /path/to/addons/my_module     # then rename strings: library_demo, library.book, library.loan
./odoo-bin -d testdb -i my_module --addons-path=... --stop-after-init
./odoo-bin -d testdb -i my_module --test-enable --test-tags /my_module --stop-after-init
```
Gotchas found while building it: manifest `data` order (actions before views that call them); `type="http"` JSON endpoints need `Content-Type: application/json`.
