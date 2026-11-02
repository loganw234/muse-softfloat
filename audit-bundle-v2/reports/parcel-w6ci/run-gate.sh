#!/usr/bin/env bash
# run-gate.sh LABEL BUDGET - run tools/run.sh in the w6-ci worktree
# with MSF_PYTHON pinned to the workspace .venv, capturing the full
# log and a normalized verdict summary (date line and elapsed
# seconds stripped) beside this script for byte comparison.
set -u
LABEL="${1:?label}"
BUDGET="${2:?budget}"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w6-ci" || exit 9
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
LOG="$WS/scratch/parcel-w6ci/gate-$LABEL-$BUDGET.log"
SUM="$WS/scratch/parcel-w6ci/gate-$LABEL-$BUDGET.summary"
bash tools/run.sh "$BUDGET" > "$LOG" 2>&1
rc=$?
echo "run.sh $BUDGET ($LABEL): exit=$rc log=$LOG"
grep -v '^date:' "$LOG" | sed 's/PASS in [0-9]*s/PASS in Ns/' > "$SUM"
tail -5 "$LOG"
exit $rc
