#!/usr/bin/env bash
# 04_regen_gates.sh - regenerate tables twice (byte-identical),
# re-watch seam controls on the final inventory, then
# tools/run.sh smoke + standard.
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg1" || exit 9
S="$WS/scratch/parcel-w5alg1"
mkdir -p "$S/out" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg1\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
PY="$MSF_PYTHON"

echo "===== gen_tables pass 1 (post-implemented) ====="
"$PY" tools/gen_tables.py > "$S/out/gen3.log" 2>&1; echo "rc=$?"
cat "$S/out/gen3.log"
mkdir -p "$S/out/gen-b"
cp include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv "$S/out/gen-b/"
echo "===== gen_tables pass 2 (byte-identical required) ====="
"$PY" tools/gen_tables.py > "$S/out/gen4.log" 2>&1; echo "rc=$?"
cat "$S/out/gen4.log"
ok=1
for pair in "include/muse_softfloat.h muse_softfloat.h" "src/msf_formats.h msf_formats.h" \
            "tests/msf_dispatch.h msf_dispatch.h" "docs/COVERAGE.tsv COVERAGE.tsv"; do
  set -- $pair
  if cmp -s "$1" "$S/out/gen-b/$2"; then echo "byte-identical: $1"; else echo "DRIFT: $1"; ok=0; fi
done
[ "$ok" = 1 ] || { echo "REGEN: FAIL"; exit 1; }

echo "===== seam controls on final inventory ====="
"$PY" "$S/check_seam.py" > "$S/out/seam_controls2.log" 2>&1; echo "rc=$?"
cat "$S/out/seam_controls2.log"

echo "===== smoke ====="
bash tools/run.sh smoke > "$S/out/smoke.log" 2>&1; echo "smoke rc=$?"
grep -E 'inventory:|tier2 planned:|alg-|mpfr-alg|VERDICT|control |total |PASS|FAIL' "$S/out/smoke.log"
tail -3 "$S/out/smoke.log"

echo "===== standard ====="
bash tools/run.sh standard > "$S/out/standard.log" 2>&1; echo "standard rc=$?"
grep -E 'VERDICT|total |PASS|FAIL' "$S/out/standard.log"
tail -3 "$S/out/standard.log"
echo "===== 04_regen_gates done ====="
