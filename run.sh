#!/bin/sh
set -eu
FRUITFLY_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export PYTHONPATH="$FRUITFLY_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
exec python -m fruitfly "$@"
