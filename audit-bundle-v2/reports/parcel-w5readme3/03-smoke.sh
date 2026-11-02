#!/usr/bin/env bash
# 03-smoke.sh - host runner totals from the front door (smoke budget).
# Also fixes probe 02 (b1): has_rm is comma-field 9, has_flags is 10.
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
ulimit -t 1800 2>/dev/null || true
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export TMPDIR=$PWD/scratch/parcel-w5readme3/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
WT=worktrees/w5-readme3
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "--- has_rm census, corrected fields ---"
awk '/static const msf_op_desc_t MSF_OPS/,/^};/ {
  if ($0 ~ /^\s*\{ "/) {
    split($0, a, ",")
    gsub(/[ \t]/, "", a[9]); gsub(/[ \t]/, "", a[10])
    tot++; if (a[9] == "1") rm++; if (a[10] == "1") fl++
  }
} END { printf "rows=%d has_rm=%d has_flags=%d\n", tot, rm, fl }' "$WT/tests/msf_dispatch.h"
echo "--- tools/run.sh smoke (worktree root) ---"
cd "$WT" || exit 9
bash tools/run.sh smoke > /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w5readme3/out/smoke.log 2>&1
rc=$?
echo "smoke exit: $rc"
tail -40 /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w5readme3/out/smoke.log
echo "--- runner verify totals (build/smoke/verify.log) ---"
grep -E '^(file|prov|total|VERDICT|manifest|inventory)' build/smoke/verify.log | tail -70
exit $rc
