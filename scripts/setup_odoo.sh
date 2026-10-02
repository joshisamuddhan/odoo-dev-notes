#!/usr/bin/env bash
# Set up ONE Odoo version in its own virtualenv (Ubuntu/Debian; needs git, python, libpq-dev etc. - see docs/13).
# usage: scripts/setup_odoo.sh <version 14..19> [python-version e.g. 3.11.9] [target-dir]
# example: scripts/setup_odoo.sh 17            -> ~/odoo-envs/odoo17 + ~/odoo-envs/odoo17-venv + ~/odoo-envs/odoo17.conf
set -euo pipefail

VER="${1:?usage: $0 <14|15|16|17|18|19> [python-version] [target-dir]}"
DIR="${3:-$HOME/odoo-envs}"

# Default Python per Odoo version (the combos verified to run on this author's machine)
case "$VER" in
  14|15|16) DEFAULT_PY="3.8.18" ;;
  17)       DEFAULT_PY="3.11.9" ;;
  18|19)    DEFAULT_PY="3.12.0" ;;
  *) echo "Unsupported version $VER"; exit 1 ;;
esac
PYV="${2:-$DEFAULT_PY}"

# Locate the python interpreter: pyenv version if present, else system pythonX.Y
if command -v pyenv >/dev/null 2>&1 && [ -x "$(pyenv root)/versions/$PYV/bin/python" ]; then
  PYBIN="$(pyenv root)/versions/$PYV/bin/python"
elif command -v "python${PYV%.*}" >/dev/null 2>&1; then
  PYBIN="$(command -v "python${PYV%.*}")"
else
  echo "Python $PYV not found. Install it first, e.g.:  pyenv install $PYV   (or: uv python install ${PYV%.*})"; exit 1
fi
echo ">> Using $($PYBIN --version) at $PYBIN"

mkdir -p "$DIR"; cd "$DIR"
SRC="odoo$VER"; VENV="odoo$VER-venv"

if [ ! -d "$SRC/.git" ] && [ ! -f "$SRC/odoo-bin" ]; then
  echo ">> Cloning Odoo $VER.0 (shallow)"
  git clone --depth 1 --branch "$VER.0" https://github.com/odoo/odoo.git "$SRC"
fi

if [ ! -d "$VENV" ]; then
  echo ">> Creating virtualenv $VENV"
  "$PYBIN" -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install --upgrade pip wheel
# Old Odoo versions (14-16) need an older setuptools for some source builds
case "$VER" in 14|15|16) python -m pip install "setuptools<66" ;; *) python -m pip install --upgrade setuptools ;; esac
echo ">> Installing requirements (this takes a few minutes)"
python -m pip install -r "$SRC/requirements.txt"

CONF="$DIR/odoo$VER.conf"
PORT="80$VER"      # 17 -> 8017 so versions can run side by side
if [ ! -f "$CONF" ]; then
cat > "$CONF" <<EOF
[options]
addons_path = $DIR/$SRC/addons
; add your custom addons folder(s) after a comma:  ,$HOME/custom_addons
db_host = False
db_port = False
db_user = $(whoami)
db_password = False
http_port = $PORT
gevent_port = 80${VER}1
; admin_passwd = change-me
EOF
fi
echo
echo ">> DONE. Run with:"
echo "   source $DIR/$VENV/bin/activate && cd $DIR/$SRC && ./odoo-bin -c $CONF -d mydb_$VER -i base --without-demo=all"
echo "   then open http://localhost:$PORT  (login admin / admin on a new DB)"
