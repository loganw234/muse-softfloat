#!/usr/bin/env bash
set -u
source "$(dirname "$0")/env.sh"
OUT="${1:-tests/vectors}"
"$MSF_PYTHON" tests/gen_vectors_aug.py "$OUT" > "$WS/scratch/parcel-w5aug/logs/gen-aug.log" 2>&1
rc=$?
echo "exit=$rc"
cat "$WS/scratch/parcel-w5aug/logs/gen-aug.log"
exit $rc
