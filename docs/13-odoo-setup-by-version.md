# Odoo Setup Guide — any version (14 → 19), with the right Python

Follow top to bottom. Written for **Ubuntu/Debian Linux** (tested on Ubuntu 24.04). Windows/Docker alternatives at the end.
An automated script does steps 4–7 for you: `scripts/setup_odoo.sh` (see section 8).

Legend: ✔ = verified from Odoo source in this workspace or run on this machine · ◇ = general knowledge, confirm if it matters.

---

## 1. Compatibility matrix — pick the Python from here

| Odoo | Minimum Python (source) ✔ | Pinned wheels in `requirements.txt` cover ✔ | **Use this** (known to run here ✔) | PostgreSQL |
|---|---|---|---|---|
| 14.0 | 3.6 (`python_requires`) | 3.6 – 3.10 | **3.8** (3.8.18) | ◇ 10+ |
| 15.0 | 3.7 | 3.7 – 3.12 | **3.8** (3.8.18) · 3.10 also fine | ◇ 10+ |
| 16.0 | 3.7 | 3.7 – 3.12 | **3.8** (3.8.18) · 3.10 also fine | ◇ 12+ |
| 17.0 | **3.10** | 3.10 – 3.13 | **3.11** (3.11.9) · 3.10 / 3.12 fine | ◇ 12+ |
| 18.0 | **3.10** | 3.10 – 3.14 | **3.12** (3.12.0) · 3.10 / 3.11 fine | ◇ 12+ |
| 19.0 | **3.10**, max **3.14** (`release.py`) | 3.10 – 3.14 | **3.12** (3.12.0) | **13+** ✔ (`MIN_PG_VERSION`) |

Rules of thumb
- **Don't use a newer Python than the table for 14/15/16.** Their pinned libraries (psycopg2 2.8, Pillow, lxml, gevent…) often have no wheels or won't compile on 3.11/3.12 — the #1 setup failure.
- Ubuntu 24.04's system Python is 3.12 → fine for 17/18/19, **not** for 14/15/16 → install 3.8/3.10 with pyenv/uv/deadsnakes (section 3).
- Ubuntu 22.04 ships 3.10 → good for 15/16/17/18 directly. Ubuntu 20.04 ships 3.8 → good for 14/15/16.
- PostgreSQL: Odoo 15, 16, 17 and 18 all ran fine on PostgreSQL **18.4** on this machine ✔; any recent PG works.
- One **virtualenv per Odoo version**. Never share a venv between versions.
- wkhtmltopdf **0.12.6 with patched Qt** is recommended for PDF reports (any 0.12.5/0.12.6 works for basic reports).
- Node.js + `rtlcss` only needed for right-to-left languages (a warning without it is harmless).

---

## 2. System packages (once)

```bash
sudo apt update
sudo apt install -y git curl wget build-essential \
  python3-dev python3-venv python3-pip \
  libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libssl-dev libpq-dev \
  libjpeg-dev zlib1g-dev libfreetype6-dev libpng-dev libffi-dev \
  postgresql postgresql-client xz-utils fontconfig xfonts-75dpi xfonts-base
# only if you will build Python with pyenv (section 3):
sudo apt install -y libbz2-dev libreadline-dev libsqlite3-dev libncursesw5-dev tk-dev liblzma-dev
# optional
sudo apt install -y node-less npm && sudo npm install -g rtlcss
```
wkhtmltopdf (reports): `sudo apt install -y wkhtmltopdf` (works, but without patched Qt) or download the `.deb` for 0.12.6 from the wkhtmltopdf releases page (Odoo repo's `debian/control` lists the dependency) and `sudo apt install ./wkhtmltox_*.deb`. Check: `wkhtmltopdf --version`.

### PostgreSQL
```bash
sudo systemctl enable --now postgresql
sudo -u postgres createuser -s "$USER"      # easiest for local dev: superuser role = your Linux user
createdb testdb && psql -l                  # works without a password via the local socket
# production-style alternative (dedicated role with password):
sudo -u postgres createuser -d -P odoo      # then in odoo.conf: db_host=localhost, db_user=odoo, db_password=...
```
Newer PostgreSQL than your distro's: add the PGDG repo (`apt.postgresql.org`) and install `postgresql-17` etc.

---

## 3. Get the right Python version (pick ONE method)

### A. pyenv (what this machine uses ✔)
```bash
curl https://pyenv.run | bash
# add to ~/.bashrc, then open a new shell:
export PYENV_ROOT="$HOME/.pyenv"; export PATH="$PYENV_ROOT/bin:$PATH"; eval "$(pyenv init -)"
pyenv install 3.8.18      # for Odoo 14/15/16   (takes a few minutes; needs the build deps from section 2)
pyenv install 3.11.9      # Odoo 17
pyenv install 3.12.0      # Odoo 18/19
pyenv versions
$(pyenv root)/versions/3.8.18/bin/python --version
```
### B. uv (fastest, no compiling)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.8 3.11 3.12
uv python list --only-installed
uv venv --python 3.8 ~/odoo-envs/odoo16-venv       # creates the venv directly (use instead of step 5's `python -m venv`)
```
### C. deadsnakes PPA (Ubuntu apt)
```bash
sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
python3.10 --version
```
### D. The system python (OK only when it matches the table)
`python3 --version` — Ubuntu 22.04 = 3.10, Ubuntu 24.04 = 3.12.

---

## 4. Download Odoo

```bash
mkdir -p ~/odoo-envs && cd ~/odoo-envs
git clone --depth 1 --branch 17.0 https://github.com/odoo/odoo.git odoo17     # use 14.0 … 19.0
```
`--depth 1` = latest commit only (small, fast). Omit it for full history. Alternative: download `https://github.com/odoo/odoo/archive/refs/heads/17.0.zip`.
Enterprise addons (`odoo/enterprise`) are a private repo — only with a licence/partner access; community is enough for tasks.
Keep your own modules **outside** the Odoo folder: `~/custom_addons/…`.

---

## 5. Create the virtualenv and install requirements

```bash
cd ~/odoo-envs
PY=$HOME/.pyenv/versions/3.11.9/bin/python        # from section 3 (or: python3.10, or `uv venv`)
$PY -m venv odoo17-venv
source odoo17-venv/bin/activate                    # prompt shows (odoo17-venv); leave with: deactivate
python --version                                   # confirm it's the right one
pip install --upgrade pip wheel
pip install "setuptools<66"                        # ONLY for Odoo 14/15/16 (old source builds)
pip install -r odoo17/requirements.txt
```
Quick check: `python -c "import psycopg2, lxml, PIL, babel, werkzeug; print('ok')"`.

Optional dev extras: `pip install watchdog` (auto-reload with `--dev=reload`), `pip install debugpy ipython`.

---

## 6. Configuration file

`~/odoo-envs/odoo17.conf`
```ini
[options]
addons_path = /home/<you>/odoo-envs/odoo17/addons,/home/<you>/custom_addons
db_host = False          ; False = local unix socket (uses your Linux user as DB role)
db_port = False
db_user = <you>          ; the role from section 2
db_password = False
http_port = 8069         ; use a different port per version to run several at once
admin_passwd = change-me ; master password for the DB manager
; proxy_mode = True      ; only behind nginx
; workers = 0            ; 0 = threaded dev mode; production: (2 x CPU) + 1
; log_level = info
; logfile = /tmp/odoo17.log
```
Use absolute paths. Create it automatically: `./odoo-bin -c odoo17.conf --save --stop-after-init -d mydb`.
TCP login instead of socket (common on servers): `db_host = localhost`, `db_user = odoo`, `db_password = ...`.

---

## 7. Run it

```bash
source ~/odoo-envs/odoo17-venv/bin/activate
cd ~/odoo-envs/odoo17
# first run: create DB + install base (no demo data)
./odoo-bin -c ~/odoo-envs/odoo17.conf -d mydb -i base --without-demo=all
# then open  http://localhost:8069   → login admin / admin  (new DB default)
# daily use:
./odoo-bin -c ~/odoo-envs/odoo17.conf -d mydb --dev=xml          # --dev=all/reload auto-reloads (needs watchdog for reload)
# install/upgrade your module
./odoo-bin -c ~/odoo-envs/odoo17.conf -d mydb -i my_module --stop-after-init
./odoo-bin -c ~/odoo-envs/odoo17.conf -d mydb -u my_module --stop-after-init
```
Stop: `Ctrl+C`. Shell/REPL: `./odoo-bin shell -c ... -d mydb`. More commands: `04-commands.md`.
Debug mode in browser: add `?debug=1` to the URL.

### Several versions side by side
Each version = own source folder + own venv + own conf + own port + own databases (a DB created by one version cannot be opened by another):
```
~/odoo-envs/odoo16  odoo16-venv  odoo16.conf (8016)  → dbs: *_16
~/odoo-envs/odoo17  odoo17-venv  odoo17.conf (8017)  → dbs: *_17
~/odoo-envs/odoo18  odoo18-venv  odoo18.conf (8018)  → dbs: *_18
```
Tip: name your databases with the version suffix so you never mix them up.

---

## 8. One-command setup (script)

```bash
scripts/setup_odoo.sh 17                     # clone + venv + requirements + conf  (Python picked from the matrix)
scripts/setup_odoo.sh 16 3.10.14             # override the Python (must be installed via pyenv or on PATH as python3.10)
scripts/setup_odoo.sh 18 "" /opt/odoo-envs   # custom target folder (keep the "" to use the default Python)
```
It prints the exact run command at the end. Needs sections 2 and 3 done first (system packages, Python, PostgreSQL role).

✔ Tested end to end on this machine (Ubuntu 24.04): `setup_odoo.sh 17` (Python 3.11.9) and `setup_odoo.sh 16` (Python 3.8.18) each cloned, built the venv, installed all requirements, and then `-i base` loaded cleanly. Versions 14, 15, 18 and 19 use the same script path but were not re-run here.

---

## 9. Windows / Docker alternatives

### Docker (fastest if Docker is installed; ◇ not run in this session)
`docker-compose.yml`
```yaml
services:
  db:
    image: postgres:16
    environment: {POSTGRES_USER: odoo, POSTGRES_PASSWORD: odoo, POSTGRES_DB: postgres}
    volumes: [pgdata:/var/lib/postgresql/data]
  odoo:
    image: odoo:17.0                # 16.0 / 17.0 / 18.0 …
    depends_on: [db]
    ports: ["8069:8069"]
    environment: {HOST: db, USER: odoo, PASSWORD: odoo}
    volumes:
      - ./custom_addons:/mnt/extra-addons      # your modules
      - odoo-data:/var/lib/odoo
volumes: {pgdata: {}, odoo-data: {}}
```
`docker compose up -d` → http://localhost:8069 · logs: `docker compose logs -f odoo` · upgrade module: `docker compose exec odoo odoo -d mydb -u my_module --stop-after-init` (stop the service first or use `docker compose run --rm odoo ...`).

### Windows (◇)
Easiest: official Windows installer from the Odoo download page (bundles Python + PostgreSQL; code under `C:\Program Files\Odoo <ver>\server`). From source: install Python (matrix), PostgreSQL, Git, Visual C++ Build Tools, wkhtmltopdf; then `py -3.11 -m venv venv`, `venv\Scripts\activate`, `pip install -r requirements.txt` (use `requirements.txt` from the same Odoo version), `python odoo-bin -c odoo.conf`. WSL2 with Ubuntu gives the exact steps of this guide.

---

## 10. Setup troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `error: externally-managed-environment` | pip outside a venv on Ubuntu 24.04 (PEP 668) | always `source <venv>/bin/activate` first |
| `ensurepip is not available` / venv creation fails | `python3-venv` missing | `sudo apt install python3-venv` (or use pyenv/uv Python) |
| `pg_config executable not found` / psycopg2 build fails | libpq headers missing | `sudo apt install libpq-dev` |
| `fatal error: Python.h: No such file` | python dev headers missing | `sudo apt install python3-dev` (pyenv builds include them) |
| `fatal error: ldap.h` / `sasl.h` / python-ldap fails | LDAP dev libs | `sudo apt install libldap2-dev libsasl2-dev` |
| `fatal error: libxml/xmlversion.h` / lxml build fails | xml dev libs | `sudo apt install libxml2-dev libxslt1-dev` |
| Pillow/psycopg2/gevent fails to build on Odoo 14–16 | Python too new (3.11/3.12) | recreate venv with the Python from the matrix (3.8/3.10) |
| `ModuleNotFoundError: No module named 'distutils'` | Python 3.12 removed distutils; old Odoo | use Python ≤ 3.11 for 14/15/16; or `pip install "setuptools<66"` on ≤3.11 |
| `pyenv install` → `BUILD FAILED` / missing `_ctypes`, `bz2`, `readline` | build deps | install the second apt block from section 2, retry |
| `FATAL: role "xyz" does not exist` | no PostgreSQL role | `sudo -u postgres createuser -s $USER` (or the `odoo` role) |
| `FATAL: Peer authentication failed` | socket login as the wrong OS user | run as the matching user, or `db_host=localhost` + password (`createuser -P`) |
| `FATAL: password authentication failed` | wrong `db_password` | fix conf, or `sudo -u postgres psql -c "ALTER USER odoo PASSWORD 'x'"` |
| `Address already in use` (8069) | another Odoo/other app | `lsof -i :8069`, kill it or set `http_port` |
| `database "x" does not exist` | typo / not created | `psql -l`; first run with `-i base` creates it |
| `OperationalError: ... new encoding (UTF8) is incompatible` | DB created from a non-UTF8 template | `createdb -E UTF8 -T template0 mydb` |
| Blank/odd UI after upgrade | stale assets | `?debug=assets`, or delete `ir_attachment` assets (`/web/assets/…`) and reload |
| PDF reports empty / ugly header-footer | wkhtmltopdf missing or not patched-Qt | install 0.12.6 patched build, check `wkhtmltopdf --version` |
| `You need to restart ... Odoo requires Python >= 3.x` | wrong interpreter in venv | `python --version` inside venv; recreate with the right one |
| Wrong DB/module after switching versions | DBs are version-bound | use a new DB per version (`mydb_17`, `mydb_18`) |
| Pip takes forever / times out | network | retry; `pip install --default-timeout=100 -r requirements.txt` |

Verify a finished install in one line: `./odoo-bin -c <conf> -d smoke_$RANDOM -i base --stop-after-init --without-demo=all && echo INSTALL_OK`, then `dropdb` it.
