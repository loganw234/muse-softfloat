#!/usr/bin/env bash
# 03_vectors.sh - generate committed alg vectors (MPFR decider x
# exact-Python cross-decision inside the generator), twice,
# byte-identical required.
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
export MSF_ALG_DECIDER="$S/out/alg_decider.exe"
[ -x "$MSF_ALG_DECIDER" ] || { echo "decider missing; run 02_kernel.sh first"; exit 1; }

echo "===== gen_vectors_alg pass 1 ====="
"$PY" tests/gen_vectors_alg.py tests/vectors > "$S/out/gen_alg1.log" 2>&1
echo "rc=$?"; cat "$S/out/gen_alg1.log"
mkdir -p "$S/out/vec-a"
cp tests/vectors/alg-f16.vec tests/vectors/alg-f32.vec tests/vectors/alg-f64.vec "$S/out/vec-a/"

echo "===== gen_vectors_alg pass 2 (byte-identical required) ====="
"$PY" tests/gen_vectors_alg.py tests/vectors > "$S/out/gen_alg2.log" 2>&1
echo "rc=$?"; cat "$S/out/gen_alg2.log"
ok=1
for f in alg-f16.vec alg-f32.vec alg-f64.vec; do
  if cmp -s "tests/vectors/$f" "$S/out/vec-a/$f"; then echo "byte-identical: $f"; else echo "DRIFT: $f"; ok=0; fi
done
[ "$ok" = 1 ] || { echo "VECTOR REGEN: FAIL"; exit 1; }

echo "===== counts ====="
wc -l tests/vectors/alg-f16.vec tests/vectors/alg-f32.vec tests/vectors/alg-f64.vec
for f in tests/vectors/alg-f16.vec tests/vectors/alg-f32.vec tests/vectors/alg-f64.vec; do
  echo "-- $f modes/tags:"; awk '!/^#/ {print $2}' "$f" | sort | uniq -c
  awk '!/^#/ {print $NF}' "$f" | sort | uniq -c
done > "$S/out/vec_counts.log" 2>&1
cat "$S/out/vec_counts.log"
echo "===== 03_vectors done ====="
