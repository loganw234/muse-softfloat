#!/usr/bin/env bash
# 18_run.sh - generator integrity: build copy decider, regenerate alg
# vectors twice, compare bytes + vs committed. Never writes into copy.
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
gcc -std=c11 -O2 -ffp-contract=off -Iinclude $SRC tests/alg_decider.c \
  -o "$OUT/alg_decider.exe" -lmpfr -lgmp 2>"$OUT/decider_build.log" \
  || { cat "$OUT/decider_build.log"; exit 1; }
echo "copy decider built"
rm -rf "$OUT/alg1" "$OUT/alg2"
MSF_ALG_DECIDER="$OUT/alg_decider.exe" MSF_PYTHON=$PY \
  $PY tests/gen_vectors_alg.py "$OUT/alg1" > "$OUT/algregen1.log" 2>&1
echo "regen1 rc=$?"; tail -2 "$OUT/algregen1.log"
MSF_ALG_DECIDER="$OUT/alg_decider.exe" MSF_PYTHON=$PY \
  $PY tests/gen_vectors_alg.py "$OUT/alg2" > "$OUT/algregen2.log" 2>&1
echo "regen2 rc=$?"; tail -2 "$OUT/algregen2.log"
for f in alg-f16.vec alg-f32.vec alg-f64.vec; do
  if cmp -s "$OUT/alg1/$f" "$OUT/alg2/$f"; then
    echo "regen byte-identical: $f"
  else
    echo "REGEN NOT BYTE-IDENTICAL: $f"
  fi
  if cmp -s "tests/vectors/$f" "$OUT/alg1/$f"; then
    echo "regen matches committed: $f"
  else
    echo "REGEN DIFFERS FROM COMMITTED: $f"
  fi
done
cd "$ROOT" || exit 9
