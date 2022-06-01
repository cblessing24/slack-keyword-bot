#! /bin/sh
set -e

cd "$(dirname "$0")"/..
./.venv/bin/flask run --port 80 --host 0.0.0.0
