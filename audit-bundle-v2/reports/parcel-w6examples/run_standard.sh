#!/usr/bin/env bash
set -u
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-examples || exit 9
LOG=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6examples/standard.log
bash tools/run.sh standard > "$LOG" 2>&1
rc=$?
echo "run.sh standard rc=$rc"
grep -E '^(== budget|date:|python:|host compiler|drift check|built |unit |manifest:|expect-counts:|file |prov |total |VERDICT|type scan|target compiler|target undefined|symbol scan|control |inventory:|negative controls|aug_exhaustive|  kind|budget )' "$LOG" || true
tail -5 "$LOG"
exit $rc
