#!/usr/bin/env bash
set -u
source "$(dirname "$0")/env.sh"
OP="${1:?op}"
bash "$WS/scratch/parcel-w5aug/scripts/exhaustive_op.sh" "$OP" > "$WS/scratch/parcel-w5aug/logs/exh-run-$OP.log" 2>&1
rc=$?
echo "exit=$rc op=$OP"
tail -25 "$WS/scratch/parcel-w5aug/logs/exh-run-$OP.log"
exit $rc
