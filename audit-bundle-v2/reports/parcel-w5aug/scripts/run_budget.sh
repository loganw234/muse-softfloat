#!/usr/bin/env bash
# usage: run_budget.sh smoke|standard LOGNAME
set -u
source "$(dirname "$0")/env.sh"
BUDGET="${1:?budget}"
LOG="$WS/scratch/parcel-w5aug/logs/${2:?logname}"
tools/run.sh "$BUDGET" > "$LOG" 2>&1
rc=$?
echo "exit=$rc log=$LOG"
tail -40 "$LOG"
exit $rc
