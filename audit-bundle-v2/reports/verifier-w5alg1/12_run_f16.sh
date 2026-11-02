#!/usr/bin/env bash
# 12_run_f16.sh - exhaustive binary16 differential: copy kernel vs my decider.
# Prints TOTAL / mismatches. Memory ceiling explicit.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
ulimit -v 4194304
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
COPY=$ROOT/worktrees/verify5-alg1
VDIR=$ROOT/scratch/verifier-w5alg1
OUT=$VDIR/out
PY=$ROOT/.venv/Scripts/python.exe
mkdir -p "$OUT"
cd "$COPY" || exit 9
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
gcc -std=c11 -O2 -ffp-contract=off -Iinclude $SRC \
  "$VDIR/11_harness.c" -o "$OUT/vharness.exe" 2>"$OUT/vharness_build.log" \
  || { cat "$OUT/vharness_build.log"; exit 1; }
echo "harness built"
"$OUT/vharness.exe" f16 > "$OUT/kern_f16.txt" 2>"$OUT/kern_f16.err"
echo "kernel sweep done rc=$? lines=$(wc -l < "$OUT/kern_f16.txt")"
cd "$ROOT" || exit 9
$PY -u "$VDIR/12_compare_f16.py"
