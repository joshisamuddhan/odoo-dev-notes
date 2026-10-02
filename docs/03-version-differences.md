# Odoo 14 → 19: what changes the syntax you type

Items marked ✔ were **verified against the Odoo source in this workspace** (odoo14…odoo19 checkouts). Others are from experience — confirm on the test machine if it matters.

## FIRST 2 MINUTES ON THEIR MACHINE: find the version
```bash
grep -n "version_info" <odoo_dir>/odoo/release.py          # exact version
ls <odoo_dir>/addons | head; ./odoo-bin --version
grep -rn "<tree\|<list" <odoo_dir>/addons/account/views/account_move_views.xml | head -2    # tree or list?
grep -c "attrs=" <odoo_dir>/addons/account/views/account_move_views.xml                      # 0 => v17+
```
Then copy syntax from a core view of THAT version (e.g. `addons/sale/views/sale_order_views.xml`). Core code is the best cheat sheet.

## Summary table
| Topic | ≤ v16 | v17 | v18 | v19 |
|---|---|---|---|---|
| List view tag ✔ | `<tree>`, view_mode `tree` | `<tree>` | **`<list>`**, view_mode `list` | `<list>` |
| Field visibility ✔ | `attrs="{'invisible': [('state','=','x')]}"`, `states="draft"` | **`invisible="state == 'x'"`** (attrs gone) | same as 17 | same |
| Hide column in list | `invisible="1"` | `column_invisible="1"` | `column_invisible="True"` | same |
| Chatter in form ✔ | `<div class="oe_chatter">…` | same | **`<chatter/>`** | `<chatter/>` |
| `name_get()` ✔ | used (deprecated in 16: `_compute_display_name`) | `_compute_display_name` | `name_get` removed | — |
| Search by name | `_name_search` | `_name_search` | `_search_display_name` | — |
| Access check ✔ | `check_access_rights('read')` + `check_access_rule` | same | **`check_access('read')`** (old ones deprecated) | — |
| Cron fields ✔ | `numbercall`, `doall` | present | **removed** | — |
| SQL constraints ✔ | `_sql_constraints = [...]` | same | same | **`name = models.Constraint("UNIQUE(x)", "msg")`** |
| JSON route type ✔ | `type='json'` | `type='json'` | `type='json'` | **`type='jsonrpc'`** (`'json'` = deprecated alias) ✔ |
| `_()` | `_("x %s") % v` | `_("x %s", v)` lazy | same | same |
| `read_group` | `read_group(domain, fields, groupby)` | **`_read_group(domain, groupby, aggregates)`** new | same (tested `["__count"]`) | same |
| Session auth | `authenticate(db, login, pw, env)` | `authenticate(db, {"login","password","type":"password"})` | same | same |
| Kanban card template ✔ | `kanban-box` | `kanban-box` | **`t-name="card"`** | `card` |
| Python | 3.7–3.10 | 3.10+ | 3.10–3.12 | 3.10+ |
| JS | OWL 1 (v14/15), OWL 2 (v16+) | OWL 2 | OWL 2 | OWL 2 |
| Groups | `res.groups` + `category_id` | same | same | `res.groups.privilege` introduced ✔ (see `base_groups.xml`) |

## Migrating a snippet between versions
- `attrs` → expression: `attrs="{'invisible': [('state','!=','draft')]}"` → `invisible="state != 'draft'"`;
  `[('a','=',1),('b','=',2)]` (AND) → `a == 1 and b == 2`; `'|'` → `or`.
- `states="draft,sent"` → `invisible="state not in ('draft','sent')"`.
- `<tree>` ↔ `<list>`; also `view_mode="tree,form"` ↔ `"list,form"`; `res.model` default views remain.
- `name_get` → `_compute_display_name`:
  ```python
  @api.depends("name", "code")
  def _compute_display_name(self):
      for rec in self:
          rec.display_name = f"[{rec.code}] {rec.name}"
  ```
- `self.env.cr.execute` still same; `self.env.user.has_group("module.group")` works everywhere (v18 also `user.has_group`).
- `fields.Date.context_today(self)` same everywhere.
- `@api.model_create_multi` — use in v14+ (single-vals create is deprecated).
- `self.env.context`/`with_context` same. `sudo()` same. `Command` from `odoo` (v17+ `from odoo import Command`; v14–16 `from odoo.fields import Command`).
- Manifest `version`: must start with the series, e.g. `"17.0.1.0.0"`.
- Controllers: `request.session.uid`, `request.env` same; `request.update_env(user=uid)` v15+ (older: `request.uid = uid`).
- Reports: `t-esc` still works but prefer `t-out` (v15+).
- Settings: `res.config.settings` + `config_parameter=` works everywhere.
- Odoo 18 domain `any`/`not any` operator is supported (also 17).
- Tests: `from odoo.tests.common import TransactionCase`, tags `@tagged('post_install', '-at_install')`.

## Run differences
- ≤ v16 DB options same. v17+ `--db_user/--db_host` unchanged. `odoo-bin shell -d db` for REPL (`env`, `self`).
- Run tests: `./odoo-bin -d test -i mymodule --test-enable --test-tags /mymodule --stop-after-init`.

## Gotchas found while testing this kit (all 4 versions: 15/16/17/18 installed fresh)
- A manifest whose `version` doesn't start with the running series (e.g. `18.0.x` on Odoo 17) breaks loading when that module sits inside a folder passed to `--addons-path` (observed on v17 and v18; Odoo 15 accepted a `16.0` manifest). Keep other-version modules out of the path.
- A **non-stored computed field used in a filter/domain** fails view validation in v18 ("Unsearchable field") — add `search=` or `store=True`.
