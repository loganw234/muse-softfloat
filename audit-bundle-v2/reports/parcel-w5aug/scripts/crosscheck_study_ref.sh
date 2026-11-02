#!/usr/bin/env bash
set -u
source "$(dirname "$0")/env.sh"
"$MSF_PYTHON" "$WS/scratch/parcel-w5aug/scripts/crosscheck_study_ref.py" > "$WS/scratch/parcel-w5aug/logs/crosscheck.log" 2>&1
rc=$?
echo "exit=$rc"
cat "$WS/scratch/parcel-w5aug/logs/crosscheck.log"
exit $rc
