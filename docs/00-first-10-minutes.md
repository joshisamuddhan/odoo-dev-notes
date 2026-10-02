# FIRST 10 MINUTES (print this / keep it open)

## 1. Who/what am I on? (2 min)
```bash
whoami; pwd; ls
ps aux | grep -i odoo-bin | grep -v grep          # is Odoo running? shows conf, addons path, db, python
which python3; python3 --version; ls -d ~/*venv* ~/*/venv 2>/dev/null
psql -l                                            # databases (try: sudo -u postgres psql -l)
```
## 2. Which Odoo version? (1 min)
```bash
grep -n "version_info" <odoo_dir>/odoo/release.py
grep -c "attrs=" <odoo_dir>/addons/account/views/account_move_views.xml     # 0 => v17+
grep -c "<list" <odoo_dir>/addons/account/views/account_move_views.xml      # >0 => v18+
grep -c "<chatter" <odoo_dir>/addons/account/views/account_move_views.xml   # >0 => v18+
```
| tag | v15/16 | v17 | v18 | v19 |
|---|---|---|---|---|
| list view | `<tree>` | `<tree>` | `<list>` | `<list>` |
| hide | `attrs=` | `invisible="expr"` | same | same |
| chatter | `<div class="oe_chatter">` | same | `<chatter/>` | `<chatter/>` |
| kanban card | `kanban-box` | `kanban-box` | `t-name="card"` | `card` |
Copy the right skeleton: `snippets/minimal_module` (18) / `_v17` / `_v16` (also OK for 15; set `15.0.x` in manifest).

## 3. Where do I put my module? (1 min)
```bash
cat <conf file>  |  grep -E "addons_path|db_|http_port"        # conf from the ps line (-c file)
mkdir -p <custom_addons> ; cp -r snippets/minimal_module_vXX <custom_addons>/my_module
```
(addons_path must include `<custom_addons>`; if not, pass `--addons-path=` on the command line, or add it to the conf.)

## 4. Prove the loop works (3 min) — before writing any real code
```bash
./odoo-bin -c <conf> -d <db> -i my_module --stop-after-init        # install  (use -u for later changes)
./odoo-bin -c <conf> -d <db>                                        # start; open http://localhost:8069
```
- Create a test DB if unsure: `createdb practice1` then `-d practice1 -i base,my_module`.
- Login: admin/admin (check with interviewer), enable `?debug=1`.
- Python change → restart. XML/field change → `-u my_module` (+ restart). Use `--dev=all` to auto-reload.
- Watch the terminal/log for ERROR lines; `tail -f /var/log/odoo/*.log` if daemonised.

## 5. Sanity questions to ask the interviewer
Which version? May I use the web/docs? May I `git init`? Which DB to use? Is a README/demo expected? Is the brief fixed or can I make assumptions?

## 6. The 5 mistakes that eat 30 minutes — avoid them
1. ACL missing (`ir.model.access.csv`) → "not allowed to access".
2. Manifest `data` order: actions/reports must load BEFORE views that call them.
3. Wrong syntax for the version (`<list>` vs `<tree>`, `attrs`).
4. Forgot `-u` after changing XML/fields (or restart after Python).
5. Non-stored compute used in a filter/domain without `search=` method (or `store=True`).

## If Odoo is NOT installed on the machine
See `docs/13-odoo-setup-by-version.md` (Python per version, venv, PostgreSQL, conf) or run `scripts/setup_odoo.sh <version>`.
