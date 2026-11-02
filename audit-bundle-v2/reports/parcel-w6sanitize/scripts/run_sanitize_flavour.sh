#!/usr/bin/env bash
# usage: run_sanitize_flavour.sh <flavour-or-default> <logfile>
set -u
FLAV="$1"; LOG="$2"
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-sanitize || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
if [ "$FLAV" = default ]; then
    unset MSF_SANITIZE
else
    export MSF_SANITIZE="$FLAV"
fi
bash tools/run.sh sanitize > "$LOG" 2>&1
rc=$?
echo "RUN_SANITIZE flavour=$FLAV rc=$rc log=$LOG"
grep -E '^(==|host compiler|canary|sanitize|control|total|VERDICT|unit:|aug_exhaustive pool|built|budget|RUN.SH)' "$LOG" > "$LOG.grep" 2>&1
cat "$LOG.grep"
exit $rc
