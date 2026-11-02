#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../../worktrees/polish-stale1" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/../../scratch/lead/tmp" TMP="$PWD/../../scratch/lead/tmp" TEMP="$PWD/../../scratch/lead/tmp"
mkdir -p "$TMPDIR"
export MSF_PYTHON="$PWD/../../.venv/Scripts/python.exe"
LOG="$PWD/../../scratch/lead/gate_polish1_standard.log"
bash tools/run.sh standard > "$LOG" 2>&1
rc=$?
echo "gate rc=$rc log=$LOG"
tail -n 25 "$LOG"
exit $rc
