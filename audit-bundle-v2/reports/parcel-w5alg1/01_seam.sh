#!/usr/bin/env bash
# 01_seam.sh - regenerate the seam twice (byte-identical), watch the
# seam negative controls, then smoke the seam tree (Git Bash).
set -u
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
echo "python: $PY ($($PY --version 2>&1))"
gcc -dumpmachine; gcc -dumpversion

echo "===== gen_tables pass 1 ====="
"$PY" tools/gen_tables.py > "$S/out/gen1.log" 2>&1; echo "rc=$?"
cat "$S/out/gen1.log"
mkdir -p "$S/out/gen-a"
cp include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv "$S/out/gen-a/"

echo "===== gen_tables pass 2 (byte-identical required) ====="
"$PY" tools/gen_tables.py > "$S/out/gen2.log" 2>&1; echo "rc=$?"
cat "$S/out/gen2.log"
ok=1
for f in muse_softfloat.h msf_formats.h msf_dispatch.h COVERAGE.tsv; do
  src="$f"
  case "$f" in
    muse_softfloat.h) src="include/muse_softfloat.h";;
    msf_formats.h) src="src/msf_formats.h";;
    msf_dispatch.h) src="tests/msf_dispatch.h";;
    COVERAGE.tsv) src="docs/COVERAGE.tsv";;
  esac
  if cmp -s "$src" "$S/out/gen-a/$f"; then echo "byte-identical: $src"; else echo "DRIFT: $src"; ok=0; fi
done
[ "$ok" = 1 ] || { echo "REGEN: FAIL"; exit 1; }

echo "===== seam controls ====="
"$PY" "$S/check_seam.py" > "$S/out/seam_controls.log" 2>&1; echo "rc=$?"
cat "$S/out/seam_controls.log"
grep -q 'SEAM CHECKS: PASS' "$S/out/seam_controls.log" || { echo "SEAM CONTROLS: FAIL"; exit 1; }

echo "===== smoke (seam tree: 6 planned rows named) ====="
bash tools/run.sh smoke > "$S/out/seam_smoke.log" 2>&1; echo "smoke rc=$?"
grep -E 'inventory:|tier2 planned:|VERDICT|control |PASS|FAIL|total' "$S/out/seam_smoke.log"
tail -3 "$S/out/seam_smoke.log"
echo "===== 01_seam done ====="
