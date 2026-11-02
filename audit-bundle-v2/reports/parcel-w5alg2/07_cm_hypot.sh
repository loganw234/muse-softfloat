#!/usr/bin/env bash
# 07_cm_hypot.sh - optional cr_hypot execution corroboration
# (foreign units compiled unopened; execution only).
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS" || exit 9
S="$WS/scratch/parcel-w5alg2"
mkdir -p "$S/out" "$S/tmp/cm"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg2\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
CM=scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94
T="$S/tmp/cm"

echo "== build foreign units (never opened) =="
gcc -std=c11  -O2 -frounding-math -ffp-contract=off -c "$CM/src/binary64/hypot/hypot.c"   -o "$T/cm_hypot64.o"  2> "$T/cm_build.log"; echo "f64 unit rc=$?"
gcc -std=c11  -O2 -frounding-math -ffp-contract=off -c "$CM/src/binary32/hypot/hypotf.c"  -o "$T/cm_hypot32.o" 2>> "$T/cm_build.log"; echo "f32 unit rc=$?"
gcc -std=gnu11 -O2 -frounding-math -ffp-contract=off -c "$CM/src/binary16/hypot/hypotf16.c" -o "$T/cm_hypot16.o" 2>> "$T/cm_build.log"; echo "f16 unit rc=$?"
wc -c "$T/cm_build.log"; cat "$T/cm_build.log"
gcc -std=gnu11 -O2 -frounding-math -ffp-contract=off -DWITH_F16 \
  "$S/cm_hypot_harness.c" "$T/cm_hypot64.o" "$T/cm_hypot32.o" "$T/cm_hypot16.o" \
  -o "$T/cm_hypot.exe" -lm 2>> "$T/cm_build.log"; echo "link rc=$?"
cat "$T/cm_build.log"

echo "== generate cases =="
"$MSF_PYTHON" "$S/cm_hypot_cases.py" gen; echo "gen rc=$?"
for M in N Z U D; do
  "$T/cm_hypot.exe" $M < "$S/out/cm_hypot_cases.txt" > "$S/out/cm_hypot_out_$M.txt"
  echo "mode $M rc=$? lines=$(wc -l < "$S/out/cm_hypot_out_$M.txt")"
done
"$MSF_PYTHON" "$S/cm_hypot_cases.py" check; echo "check rc=$?"
