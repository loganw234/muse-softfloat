#!/usr/bin/env bash
set -u
BUDGET="${1:-standard}"
TAG="${2:-main}"
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
LOG="/c/Users/logan/source/repos/Muse-Softfloat/scratch/lead/$TAG-$BUDGET.log"
bash tools/run.sh "$BUDGET" > "$LOG" 2>&1
rc=$?
echo "run.sh $BUDGET rc=$rc log=$LOG"
grep -E '^(== budget|python:|host compiler:|drift check:|total |VERDICT|type scan:|symbol scan:|control tier|inventory:|negative controls:|budget |RUN.SH)' "$LOG" || true
tail -5 "$LOG"
exit $rc
