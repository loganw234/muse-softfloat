#!/usr/bin/env bash
# 02-probes.sh - light proofs before any edit:
#  (a) site/build_data.py as committed fails at base (pair_call regex)
#  (b) dispatch has_rm census; aug raw vs counted lines
#  (c) .gitignore covers build/ (gate outputs stay uncommitted)
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
ulimit -t 600 2>/dev/null || true
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export TMPDIR=$PWD/scratch/parcel-w5readme3/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
mkdir -p scratch/parcel-w5readme3/out
WT=worktrees/w5-readme3
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"

echo "--- (a) build_data.py as committed (expect refusal) ---"
"$MSF_PYTHON" "$WT/site/build_data.py" > scratch/parcel-w5readme3/out/build_data-atbase.log 2>&1
echo "exit: $?"
cat scratch/parcel-w5readme3/out/build_data-atbase.log

echo "--- (b1) dispatch has_rm census (awk over MSF_OPS rows) ---"
awk '/static const msf_op_desc_t MSF_OPS/,/^};/ {
  if ($0 ~ /^\s*\{ "/) {
    # fields after argkinds: nargs, has_rm, has_flags, status, wave
    n = split($0, a, ",")
    # a[] layout: name,std,sig,retk, {ak0,ak1,ak2}, nargs, has_rm, ...
    gsub(/[ \t]/, "", a[9]); gsub(/[ \t]/, "", a[10])
    tot++; if (a[10] == "1") rm++
  }
} END { printf "rows=%d has_rm=1: %d\n", tot, rm }' "$WT/tests/msf_dispatch.h"

echo "--- (b2) aug files raw lines vs counted lines ---"
for f in aug-f16 aug-f32 aug-f64 explog-f16 explog-f32 explog-f64; do
  raw=$(wc -l < "$WT/tests/vectors/$f.vec")
  counted=$(awk '!/^#/ && NF>0 {c++} END {print c+0}' "$WT/tests/vectors/$f.vec")
  comments=$(awk '/^#/ {c++} END {print c+0}' "$WT/tests/vectors/$f.vec")
  echo "$f.vec raw=$raw counted=$counted comment_lines=$comments"
done

echo "--- (c) .gitignore ---"
cat "$WT/.gitignore"
git -c "safe.directory=$PWD/$WT" -C "$WT" check-ignore -v build/smoke/verify.log || echo "build/ NOT ignored (gate outputs would dirty status - clean after runs)"
echo "--- worktree status (must still be clean) ---"
git -c "safe.directory=$PWD/$WT" -C "$WT" status --short
echo "PROBES DONE"
