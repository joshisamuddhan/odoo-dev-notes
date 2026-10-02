# Quality checklist — run through it in the last 20 minutes

## Security
- [ ] ACL line for every model (incl. TransientModel wizards); least privilege (no `unlink` for normal users)
- [ ] Groups + `implied_ids`; menus restricted with `groups=`
- [ ] Record rules where users should see only their records / their company
- [ ] No `sudo()` unless justified (and scoped to the minimum recordset)
- [ ] No SQL string formatting with user input → params
- [ ] API: authenticated, whitelisted writable fields, size limits on `limit`, no secrets in logs/responses
- [ ] `csrf=False` only on token-authenticated routes
- [ ] File uploads validated (extension allow-list, size)
- [ ] XSS: use `t-out`/`t-field` (escaped); don't build HTML from user text; `Markup` only for trusted
- [ ] Passwords/keys not hardcoded (use `ir.config_parameter` or env vars)
- [ ] Sensitive fields `groups="..."`

## Data integrity
- [ ] Constraints: `@api.constrains` / SQL constraints for uniqueness, dates, positive amounts
- [ ] `ondelete="restrict"` where deleting parent would lose history
- [ ] State transitions guarded (`if rec.state != 'draft': raise UserError`)
- [ ] Multi-record safe (`for rec in self`)
- [ ] Defaults and required fields sensible; `copy=False` for unique/sequence fields
- [ ] Multi-company: `company_id` + rule + `check_company=True`

## Performance
- [ ] No search/browse in loops (use `in` + `mapped`/`read_group`)
- [ ] Computed fields have precise `@api.depends`; `store=True` where you search/group
- [ ] Index on frequently filtered columns
- [ ] Cron batches + commit; avoid loading everything
- [ ] Pagination in lists/APIs

## Maintainability
- [ ] Small methods, clear names, docstrings for non-obvious logic
- [ ] No dead code / commented blocks / debug `print`
- [ ] Translatable strings use `_()`
- [ ] Logging (`_logger`) not `print`
- [ ] Tests for the key flows (`tests/`)
- [ ] README with assumptions

## UX
- [ ] Statusbar/buttons visible only in right states · helpful error messages · smart buttons · search filters + group by · sensible default order · demo data
