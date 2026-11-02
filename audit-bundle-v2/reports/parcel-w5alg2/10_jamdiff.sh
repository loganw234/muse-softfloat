#!/usr/bin/env bash
# 10_jamdiff.sh - JAM-mutant decider differential (expected PASS:
# packed equivalence evidence at volume, design addendum).
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg2" || exit 9
S="$WS/scratch/parcel-w5alg2"
mkdir -p "$S/out" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg2\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -DMSF_ALG_TEST_JAM \
  $SRC tests/alg_decider.c -o "$S/out/alg_decider_jam.exe" -lmpfr -lgmp \
  > "$S/out/build_jamdec.log" 2>&1; echo "build rc=$?"; cat "$S/out/build_jamdec.log"
D="$S/out/alg_decider_jam.exe"
"$D" hseed f64 20261028 100000; echo "f64 rc=$?"
"$D" hseed f32 20261028 100000; echo "f32 rc=$?"
"$D" h16seed 20261028 100000; echo "f16 rc=$?"
