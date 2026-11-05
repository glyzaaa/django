#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then python3 scripts/bootstrap.py; fi
.venv/bin/python scripts/bootstrap.py --quiet
exec .venv/bin/python scripts/run.py serve "$@"
