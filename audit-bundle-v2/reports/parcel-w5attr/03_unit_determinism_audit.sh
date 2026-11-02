#!/usr/bin/env bash
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-attr" || exit 9
S="$WS/scratch/parcel-w5attr"
mkdir -p "$S/out" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5attr\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
PY="$MSF_PYTHON"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c"

echo "===== string unit probe ====="
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -Iinclude \
  "$S/string_ta_unit.c" $SRC -o "$S/out/string_ta_unit.exe" \
  > "$S/out/build_unit.log" 2>&1
echo "build rc=$?"; cat "$S/out/build_unit.log"
"$S/out/string_ta_unit.exe" > "$S/out/string_ta_unit.log" 2>&1
echo "unit rc=$?"; cat "$S/out/string_ta_unit.log"

echo "===== determinism: two regenerations byte-compare ====="
for run in regen1 regen2; do
  mkdir -p "$S/out/$run/vec" "$S/out/$run/gen"
  "$PY" tools/gen_tables.py "$S/out/$run/gen" > "$S/out/$run/gen_tables.log" 2>&1
  echo "$run gen_tables rc=$?"
  for g in gen_vectors gen_vectors_f16 gen_vectors_f32 gen_vectors_f64 gen_vectors_xf gen_vectors_str; do
    "$PY" "tests/$g.py" directed "$S/out/$run/vec" > "$S/out/$run/$g.log" 2>&1
    echo "$run $g rc=$?"
  done
  MSF_TRIG_DECIDER="$S/out/trig_exhaustive.exe" "$PY" tests/gen_vectors_trig.py "$S/out/$run/vec" > "$S/out/$run/trig.log" 2>&1
  echo "$run trig rc=$?"
done
fail=0
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  cmp -s "$S/out/regen1/gen/$f" "$S/out/regen2/gen/$f" || { echo "DETERMINISM DIFF: $f (run1 vs run2)"; fail=1; }
  cmp -s "$f" "$S/out/regen1/gen/$f" || { echo "DETERMINISM DIFF: $f (committed vs regen1)"; fail=1; }
done
for f in "$S/out/regen1/vec"/*.vec; do
  b=$(basename "$f")
  cmp -s "$f" "$S/out/regen2/vec/$b" || { echo "DETERMINISM DIFF: $b (run1 vs run2)"; fail=1; }
  cmp -s "tests/vectors/$b" "$f" || { echo "DETERMINISM DIFF: $b (committed vs regen1)"; fail=1; }
done
[ "$fail" -eq 0 ] && echo "determinism: ALL BYTE-IDENTICAL" || echo "determinism: FAIL"

echo "===== rm-switch audit in src (third-site watch) ====="
grep -rn "MSF_IROUND" src include > "$S/out/audit_iround.log" 2>&1
wc -l "$S/out/audit_iround.log"
grep -rn "TIES_TO_AWAY" src include
echo "--- switch (rm) sites ---"
grep -rn "switch (rm)\|switch (mode)\|rm ==" src | head -60
