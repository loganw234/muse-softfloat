#!/usr/bin/env bash
# 03_vectors.sh - generate committed alg vectors twice
# (byte-identical required); rSqrt lines must match the
# pre-parcel committed files exactly.
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg2" || exit 9
S="$WS/scratch/parcel-w5alg2"
mkdir -p "$S/out/vec-a" "$S/out/vec-orig" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg2\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
PY="$MSF_PYTHON"
export MSF_ALG_DECIDER="$S/out/alg_decider.exe"
[ -x "$MSF_ALG_DECIDER" ] || { echo "decider missing; run 02_decider.sh first"; exit 1; }

# snapshot pre-parcel committed vectors for the rSqrt prefix check
git show HEAD:tests/vectors/alg-f16.vec > "$S/out/vec-orig/alg-f16.vec"
git show HEAD:tests/vectors/alg-f32.vec > "$S/out/vec-orig/alg-f32.vec"
git show HEAD:tests/vectors/alg-f64.vec > "$S/out/vec-orig/alg-f64.vec"

echo "===== gen pass 1 ====="
time "$PY" tests/gen_vectors_alg.py tests/vectors > "$S/out/gen1.log" 2>&1
echo "rc=$?"; cat "$S/out/gen1.log"
cp tests/vectors/alg-f16.vec tests/vectors/alg-f32.vec tests/vectors/alg-f64.vec "$S/out/vec-a/"

echo "===== gen pass 2 (byte-identical required) ====="
"$PY" tests/gen_vectors_alg.py tests/vectors > "$S/out/gen2.log" 2>&1
echo "rc=$?"; cat "$S/out/gen2.log"
ok=1
for f in alg-f16.vec alg-f32.vec alg-f64.vec; do
  if cmp -s "tests/vectors/$f" "$S/out/vec-a/$f"; then echo "byte-identical: $f"; else echo "DRIFT: $f"; ok=0; fi
done
[ "$ok" = 1 ] || { echo "VECTOR REGEN: FAIL"; exit 1; }

echo "===== rSqrt prefix preserved vs pre-parcel files ====="
for f in alg-f16.vec alg-f32.vec alg-f64.vec; do
  grep '_r_sqrt' "$S/out/vec-orig/$f" > "$S/out/vec-orig/$f.r"
  grep '_r_sqrt' "tests/vectors/$f" > "$S/out/vec-a/$f.r"
  if cmp -s "$S/out/vec-orig/$f.r" "$S/out/vec-a/$f.r"; then
    echo "rSqrt lines identical: $f ($(wc -l < "$S/out/vec-a/$f.r"))"
  else
    echo "RSQRT LINES CHANGED: $f"; diff "$S/out/vec-orig/$f.r" "$S/out/vec-a/$f.r" | head -5; ok=0
  fi
done
[ "$ok" = 1 ] || { echo "PREFIX CHECK: FAIL"; exit 1; }

echo "===== counts ====="
wc -l tests/vectors/alg-f16.vec tests/vectors/alg-f32.vec tests/vectors/alg-f64.vec
for f in tests/vectors/alg-f16.vec tests/vectors/alg-f32.vec tests/vectors/alg-f64.vec; do
  echo "-- $f hypot lines by mode/tag:"
  grep '_hypot' "$f" | awk '{print $2}' | sort | uniq -c
  grep '_hypot' "$f" | awk '{print $NF}' | sort | uniq -c
done > "$S/out/vec_counts.log" 2>&1
cat "$S/out/vec_counts.log"
echo "===== tie-line evidence (f16 study tie) ====="
grep -n 'mpfr-alg:ties' tests/vectors/alg-f16.vec | head -30
echo "===== 03_vectors done ====="
