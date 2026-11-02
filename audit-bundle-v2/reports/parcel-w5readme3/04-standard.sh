#!/usr/bin/env bash
# 04-standard.sh - standard gate totals (generated vectors + aug pool).
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
ulimit -t 1800 2>/dev/null || true
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export TMPDIR=$PWD/scratch/parcel-w5readme3/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
OUT=$PWD/scratch/parcel-w5readme3/out
cd worktrees/w5-readme3 || exit 9
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
bash tools/run.sh standard > "$OUT/standard.log" 2>&1
rc=$?
echo "standard exit: $rc"
grep -E '^(budget|inventory|file|total|VERDICT|aug_exhaustive|  kind|wrote|dropped)' "$OUT/standard.log" | head -40
echo "--- generated file counted lines ---"
for f in build/standard/f16-exhaustive.vec build/standard/pack-sweep.vec; do
  awk -v f="$f" '!/^#/ && NF>0 {c++} END {print f": "c+0}' "$f"
done
echo "--- verify-standard totals ---"
grep -E '^(file|prov|total|VERDICT)' build/standard/verify-standard.log
echo "--- aug pool log ---"
cat build/standard/aug-pool.log
exit $rc
