#!/usr/bin/env bash
set -u
BUDGET="${1:-smoke}"
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-seam || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
LOG="/c/Users/logan/source/repos/Muse-Softfloat/scratch/lead/w4-seam-$BUDGET.log"
bash tools/run.sh "$BUDGET" > "$LOG" 2>&1
rc=$?
echo "run.sh $BUDGET rc=$rc log=$LOG"
grep -E '^(== budget|date:|python:|semantics:|host compiler:|drift check:|built |unit |manifest:|expect-counts:|file |prov |total |VERDICT|type scan:|target compiler:|target undefined|symbol scan:|control |inventory:|tier2 planned:|negative controls:|RUN.SH)' "$LOG" || true
tail -20 "$LOG"
exit $rc
