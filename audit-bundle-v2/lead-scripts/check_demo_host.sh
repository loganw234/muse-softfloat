#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../../worktrees/w6-judgemap" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/../../scratch/lead/tmp" TMP="$(cygpath -w "$PWD/../../scratch/lead/tmp")" TEMP="$TMP"
mkdir -p "$TMPDIR"
export MSF_PYTHON="$PWD/../../.venv/Scripts/python.exe"
LOG="$PWD/../../scratch/lead/demo_host_after_fix.log"
bash demo/run_demo.sh host > "$LOG" 2>&1
rc=$?
echo "demo rc=$rc"
grep -E "PASS|FAIL|IAS15|KissFFT|interval" "$LOG" | tail -n 14
exit $rc
