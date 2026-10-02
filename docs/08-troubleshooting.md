# Troubleshooting — error → cause → fix

| Error / symptom | Usual cause | Fix |
|---|---|---|
| `You are not allowed to access 'X' (x.model) records` | no ACL line for the model/group | add row in `ir.model.access.csv` (model id = `model_x_model`), `-u` module, user must be in group |
| `External ID not found in the system: mod.xmlid` | file load ORDER in manifest, typo, module missing from `depends` | reorder `data` (actions/reports before views using them), check `depends` |
| `ParseError ... while parsing file.xml:LINE` | bad XML / field not in model / invalid view expression | look at last lines of traceback; check field names exist; matching tags; `attrs` used in v17+ |
| `Invalid field 'x' on model 'y'` (view) | field missing/typo or dependency module not installed | add field/depends |
| `Field 'x' used in domain/attrs must be in view` (older) | field referenced in `attrs/domain` not in form | add `<field name="x" invisible="1"/>` |
| `Unknown field "x" in "invisible"` / `Invalid view` (v17+) | `invisible="x == 1"` uses field absent in view | include the field in the view |
| `ValueError: Wrong value for ... selection` | write value not in Selection | use valid key |
| `ERROR: duplicate key value violates unique constraint` | `_sql_constraints` hit | catch/validate earlier or friendly message |
| `null value in column "x" violates not-null` | `required=True` field missing in `create` | pass value or give `default` |
| `AttributeError: 'x.model' object has no attribute 'y'` | method/field missing, wrong model, singleton | check names, inherited model, `ensure_one` |
| `ValueError: Expected singleton: x.model(1, 2)` | accessing a field on a multi-record set | loop `for rec in self` / `ensure_one()` |
| `RecursionError` in compute | compute writes to field it depends on | don't write inside compute; assign only the computed field |
| `Compute method failed to assign x.model(1).f` | not every record assigned in `_compute` | set default (`rec.f = 0`) for every branch |
| `TypeError: create() got multiple values` / `ValidationError creating` | `create` signature (vals_list) | `@api.model_create_multi` and iterate |
| Change not visible after code edit | server not restarted / module not upgraded | restart (python) · `-u module` (xml/model/fields) · hard refresh browser |
| `ModuleNotFoundError: No module named 'x'` | pip dependency missing | `pip install x` in Odoo's venv |
| `odoo.exceptions.MissingError: Record does not exist` | deleted record referenced | `.exists()` |
| 500 on controller | exception swallowed / wrong auth env | read server log; with `auth='none'` you need `request.update_env(user=...)` |
| API POST body empty | client sent form content-type (curl `-d` default) | send `Content-Type: application/json` (we hit this ourselves) |
| `session expired` / CSRF error on POST | `csrf` default True for `type='http'` | `csrf=False` for token APIs |
| `database "x" does not exist` | wrong `-d` | `psql -l` |
| `Address already in use` 8069 | another Odoo running | `lsof -i :8069`, kill or `--http-port=8070` |
| Wrong DB selected / DB manager shown | multiple DBs, no `-d` | pass `-d dbname` / `db_name` in conf, `--db-filter` |
| Report blank / PDF fails | wkhtmltopdf missing/wrong; QWeb error | `wkhtmltopdf --version`; view HTML at `/report/html/<report_name>/<id>`; check traceback |
| Menu not visible | group on menu, no action, or user not in group | check `groups`, parent, action, user rights |
| Field not visible in form | not added to view, `groups`, `invisible` expr | check view arch in debug → Edit View |
| onchange not firing | field not in view, wrong name | include in view; use compute instead |
| Translation not applied | `-i` vs `-u`, `.po` not loaded | `-u module -l xx`, check `i18n/` |
| Cron not running | server started with `--max-cron-threads=0`, inactive, wrong user | check `ir.cron` active/next run; run manually from UI |
| Email not sent | no outgoing mail server / queue | Settings → Technical → Emails; run "Mail: queue" cron; use `force_send=True` for tests |
| Slow list view | N+1 compute, unstored compute, missing index | `--log-sql`, store computed, `read_group`, index |
| `psycopg2.errors.InFailedSqlTransaction` | earlier SQL error in same transaction | wrap risky bit in `with self.env.cr.savepoint():` |
| `SerializationFailure/concurrent update` | two transactions same row | retry; avoid long transactions in cron; batch commits |
| `Access to this model is restricted` for portal/public user in controller | env user is public | `sudo()` narrowly or auth='user' |
| `TypeError: Object of type date is not JSON serializable` | json.dumps with dates | `json.dumps(x, default=str)` |

## Reading a traceback
1. Bottom line = actual error. 2. Walk up to the first line inside YOUR module path → the offending line. 3. If it's in `loading`/`convert`/`ParseError` → data file issue (XML). 4. In `registry`/`models` at install → field/constraint definition.

## Debug workflow
reproduce → minimal test in `odoo-bin shell` → add `_logger.info` / `breakpoint()` → fix → add test → upgrade module → verify.

## Safe-state tricks
- DB corrupted by experiments: `createdb -T clean_copy testdb` (keep a clean backup DB before starting).
- Module won't install / half-broken state: fix the error, then `dropdb` + recreate and `-i` again — faster than repairing a DB in a timed task.
- Always keep the UI logged in a second tab as admin; run unit tests in a separate DB.
