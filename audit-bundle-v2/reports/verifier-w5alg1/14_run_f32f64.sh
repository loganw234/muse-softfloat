#!/usr/bin/env bash
# 14_run_f32f64.sh - directed+seeded volume differential, f32 and f64.
# Prints counts per format. Memory ceiling explicit.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
ulimit -v 4194304
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
VDIR=$ROOT/scratch/verifier-w5alg1
OUT=$VDIR/out
PY=$ROOT/.venv/Scripts/python.exe
mkdir -p "$OUT"
cd "$ROOT" || exit 9
$PY -u "$VDIR/13_inputs.py" f32 20000 20261028
$PY -u "$VDIR/13_inputs.py" f64 20000 20261028
"$OUT/vharness.exe" list f32 "$OUT/inputs_f32.txt" > "$OUT/kern_f32.txt" 2>"$OUT/kern_f32.err"
echo "f32 sweep rc=$? lines=$(wc -l < "$OUT/kern_f32.txt")"
"$OUT/vharness.exe" list f64 "$OUT/inputs_f64.txt" > "$OUT/kern_f64.txt" 2>"$OUT/kern_f64.err"
echo "f64 sweep rc=$? lines=$(wc -l < "$OUT/kern_f64.txt")"
$PY -u "$VDIR/14_compare.py" f32
$PY -u "$VDIR/14_compare.py" f64
