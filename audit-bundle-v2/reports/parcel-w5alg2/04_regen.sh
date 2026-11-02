#!/usr/bin/env bash
# 04_regen.sh - regenerate tables in-tree twice (byte-stable),
# show what changed.
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg2" || exit 9
S="$WS/scratch/parcel-w5alg2"
mkdir -p "$S/out/gen-a" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg2\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
PY="$MSF_PYTHON"

echo "===== regen in-tree pass 1 ====="
"$PY" tools/gen_tables.py > "$S/out/gen_tables1.log" 2>&1; echo "rc=$?"
cat "$S/out/gen_tables1.log"
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  mkdir -p "$S/out/gen-a/$(dirname "$f")"
  cp "$f" "$S/out/gen-a/$f"
done
echo "===== regen pass 2 (byte-identical required) ====="
"$PY" tools/gen_tables.py > "$S/out/gen_tables2.log" 2>&1; echo "rc=$?"
ok=1
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  if cmp -s "$f" "$S/out/gen-a/$f"; then echo "byte-identical: $f"; else echo "DRIFT: $f"; ok=0; fi
done
[ "$ok" = 1 ] || { echo "TABLE REGEN: FAIL"; exit 1; }
echo "===== changed vs HEAD ====="
git status --porcelain
echo "===== hypot rows in COVERAGE ====="
grep hypot docs/COVERAGE.tsv
grep -c . docs/COVERAGE.tsv
