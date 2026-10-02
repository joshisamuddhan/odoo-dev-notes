# Commands you will need (copy/paste)

## Odoo server
```bash
# run (dev)
./odoo-bin -c odoo.conf -d mydb --dev=all
./odoo-bin -d mydb --addons-path=addons,/path/to/custom --db_user=odoo --db_password=odoo --http-port=8069
# create DB + install module
./odoo-bin -d newdb -i base,my_module --without-demo=all --stop-after-init
# upgrade module(s) / all
./odoo-bin -d mydb -u my_module[,other] --stop-after-init
./odoo-bin -d mydb -u all --stop-after-init
# tests
./odoo-bin -d testdb -i my_module --test-enable --test-tags /my_module --stop-after-init
./odoo-bin -d testdb -u my_module --test-tags .test_method_name,/my_module:TestClass.test_x --stop-after-init
# python shell (env, self available)
./odoo-bin shell -d mydb --addons-path=...      # env['res.partner'].search([]);  env.cr.commit() to persist
# logs / verbosity
--log-level=debug|info|warn   --log-handler=odoo.addons.my_module:DEBUG   --logfile=/tmp/odoo.log
# workers / limits (prod style)
--workers=4 --max-cron-threads=2 --limit-memory-soft=2147483648 --limit-time-real=120 --proxy-mode
# generate config
./odoo-bin -c odoo.conf --save --stop-after-init
# scaffold
./odoo-bin scaffold my_module /path/to/addons
# i18n
./odoo-bin -d mydb --i18n-export=/tmp/my.po --modules=my_module -l gu_IN --stop-after-init
./odoo-bin -d mydb --i18n-import=my.po -l gu_IN --i18n-overwrite --stop-after-init
```
Virtualenv: `source venv/bin/activate` (find it: `ls`, `which python3`, `ps aux | grep odoo`).
Find how Odoo is already started: `ps aux | grep odoo-bin` (shows conf/paths) and `cat /etc/odoo/*.conf`.

## odoo.conf essentials
```ini
[options]
addons_path = /opt/odoo/addons,/opt/custom
db_host = localhost
db_user = odoo
db_password = ***
admin_passwd = ***
http_port = 8069
workers = 0          ; 0 = threaded dev mode
proxy_mode = True    ; behind nginx
list_db = False
```

## PostgreSQL
```bash
psql -l                          # list DBs
psql mydb                        # connect (sudo -u postgres psql mydb if needed)
createdb mydb;  dropdb mydb
createdb -T template_db newdb    # copy DB (needs no active connections to template)
pg_dump -Fc mydb > mydb.dump ;  pg_restore -d newdb --no-owner mydb.dump
pg_dump mydb | gzip > mydb.sql.gz ; gunzip -c mydb.sql.gz | psql newdb
```
Inside psql: `\dt *partner*` tables · `\d res_partner` columns · `\x` expanded · `\timing` · `\q`.
Reset admin password: v14 accepted plaintext via SQL (`UPDATE res_users SET password='admin' WHERE login='admin';`) but **v18 does not** (plaintext scheme removed) — use the shell: `env['res.users'].browse(2).password = 'admin'; env.cr.commit()`.
Install state: `SELECT name, state, latest_version FROM ir_module_module WHERE name='my_module';`
Kill connections: `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='mydb' AND pid<>pg_backend_pid();`

## Git
```bash
git init; git add -A; git commit -m "feat: ..."; git log --oneline -10; git status; git diff
git checkout -b feature/x; git switch main; git merge feature/x; git stash / git stash pop
git rebase -i HEAD~3 (interactive; may not be available); git cherry-pick <sha>; git revert <sha>
git remote -v; git clone <url>; git pull --rebase; git push -u origin branch
```

## Linux
```bash
ls -la; cd; pwd; cat; less +F file.log (follow); tail -f /var/log/odoo/odoo.log; grep -rn "text" dir --include=*.py
find . -name "*.xml" | head;  ps aux | grep odoo;  kill <pid>;  lsof -i :8069 (who uses the port)
systemctl status|restart odoo;  journalctl -u odoo -f;  chmod/chown;  df -h; free -h; top/htop
curl -i -X POST url -H "Content-Type: application/json" -H "Authorization: Bearer KEY" -d '{"a":1}'
```
Editors: vim `i` insert, `Esc :wq` save, `:q!` quit; nano `Ctrl+O` save `Ctrl+X` exit; VS Code/PyCharm if installed.

## Debugging in Odoo
- `import pdb; pdb.set_trace()` (run server in foreground) / `breakpoint()`
- `_logger.info("vals=%s", vals)` and tail the log
- Developer mode `?debug=1` → bug icon → View Metadata / Edit View / Fields list
- `odoo-bin shell` to test ORM expressions quickly
- Check SQL queries: `--log-sql` (v18) or `--log-level=debug_sql`
