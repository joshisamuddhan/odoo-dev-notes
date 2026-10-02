# 3-Hour Practical Task — Playbook

## Before you touch the keyboard (first 15 min)
1. Read the whole brief twice. Underline every noun (→ models/fields) and every verb (→ methods/buttons/endpoints).
2. Write on paper: **MUST** list (explicitly asked) / **SHOULD** (obviously implied) / **NICE** (extras).
3. Ask the interviewer (good sign, not weakness):
   - Which Odoo version and edition? Which DB / addons path? How do I restart/upgrade?
   - Is a UI expected, API, report, or all?  Any naming/format conventions?
   - Is it OK to use documentation/web search? (They said internet is available.)
   - What does "done" look like: demo, code, tests?
   - Can I make reasonable assumptions and note them?
4. Check the environment (5 min): version, `ls` addons, how Odoo is started, DB name, editor, git. See `04-commands.md`.

## Timeline (180 min)
| Min | Do |
|---|---|
| 0–15 | Read, ask, list MUST/SHOULD/NICE |
| 15–30 | Design: models + fields + relations + states + security + views (sketch on paper) |
| 30–45 | Scaffold module (copy `snippets/library_demo` structure), manifest, install an empty module successfully |
| 45–100 | Models + constraints + business methods (MUST features). **Install/upgrade after every small step** |
| 100–130 | Views, menus, security, buttons |
| 130–155 | SHOULD features: report/API/wizard/cron as requested; sample data |
| 155–170 | Edge cases, validation, test the happy + failing path manually, fix lint |
| 170–180 | README (what/how to run/assumptions/next steps), demo script ready |

Rules of thumb: working end-to-end by minute 90. Never leave the module uninstallable. Commit often (`git init` if allowed).

## Build order that avoids pain
1. `__manifest__.py` + empty models → install (proves environment works)
2. Model + fields → add ACL CSV immediately (else "not allowed to access")
3. Menu + action + list/form view → open it in the browser
4. Business logic methods + buttons + statusbar
5. Constraints / validation messages
6. Security groups + record rules
7. Reports, wizard, cron, mail, API
8. Demo/seed data (`demo/` or `data/` xml) so the demo isn't an empty screen

## Upgrade loop
```bash
./odoo-bin -c <conf> -d <db> -u my_module --stop-after-init   # then restart server (or run with --dev=xml,reload)
```
`--dev=all` (or `--dev=xml,reload`) reloads python/xml automatically (v14+; `--dev=reload` needs `watchdog`).
XML-only change: just refresh page with `?debug=1` when `--dev=xml`, otherwise `-u` needed.
Python change: restart server (or `--dev=reload`). New field: `-u` needed.

## What interviewers usually score
- Does it work end-to-end and can you demo it?
- Correct Odoo structure (manifest, ACL, views, naming), no hacks
- Validation & error messages; sensible state machine
- Security (groups, record rules, no SQL injection, no unnecessary sudo)
- Clean code/readability, small methods, comments only where useful
- How you think: talk through trade-offs, mention what you'd do with more time
- Handling of ambiguity and time management

## Naming conventions
- Module: `snake_case`, prefix with project (`hr_leave_ext`); model `x.thing` (dots), table `x_thing`.
- Methods: `action_*` buttons, `_compute_*`, `_check_*` constraints, `_onchange_*`, `_cron_*`, private helpers `_`.
- XML ids: `view_<model>_form`, `action_<model>`, `menu_<model>`, `group_<module>_<role>`, `rule_...`.
- Files: `models/<model_name>.py`, `views/<model_name>_views.xml`.

## Final README template (paste into module README.md)
```
# <Module name>
## What it does
## Install
./odoo-bin -d <db> -i <module>      (depends: ...)
## Features implemented
- [x] ... (MUST)  - [x] ... (SHOULD)  - [ ] ... (not done)
## Assumptions
## Security (groups / rules)
## How to test (steps / curl examples / unit tests)
## Next steps if I had more time
```

## If you get stuck
- Error in log: read the LAST lines of the traceback, then the first line of the final exception; see `08-troubleshooting.md`.
- Don't spend >10 min on one thing: simplify, stub, move on, return later.
- Search order: core Odoo source in same version → docs → OCA repo → web.
- Say it aloud: "I'm checking how core does X in this version" — a normal senior habit.

## Mental checklist before saying "done"
[ ] Module installs on a fresh DB from scratch (`-i`, not just `-u`)  [ ] ACL for every model incl. wizards
[ ] Views open without errors (list, form, search)  [ ] Buttons work and states can't go backwards illegally
[ ] Constraints raise clear messages  [ ] No debug prints/commented junk  [ ] README + demo data
[ ] Edge cases: empty values, duplicates, wrong state, multi-record `self`, no access user
