#!/usr/bin/env bash
# 02_replay_regen.sh - replay committed xf vectors; regen to temp and byte-compare
set -uo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/verifier-w2xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w2xf\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$ROOT/worktrees/verify2-xf" || exit 9
echo "== replay committed xf vectors with copy runner =="
./build/smoke/msf_runner.exe verify tests/vectors/arith-xf.vec tests/vectors/fma-sqrt-xf.vec \
  tests/vectors/conv-xf.vec tests/vectors/compare-xf.vec tests/vectors/traps-xf.vec \
  > "$ROOT/scratch/verifier-w2xf/replay-xf.log" 2>&1
echo "verify exit=$?"
cat "$ROOT/scratch/verifier-w2xf/replay-xf.log"
echo "== regenerate to temp =="
PY="$ROOT/.venv/Scripts/python.exe"
rm -rf "$ROOT/scratch/verifier-w2xf/regen/xf"
mkdir -p "$ROOT/scratch/verifier-w2xf/regen/xf"
time "$PY" tests/gen_vectors_xf.py directed "$ROOT/scratch/verifier-w2xf/regen/xf"
echo "regen exit=$?"
echo "== byte compare =="
for f in arith-xf.vec fma-sqrt-xf.vec conv-xf.vec compare-xf.vec traps-xf.vec; do
  if cmp -s "tests/vectors/$f" "$ROOT/scratch/verifier-w2xf/regen/xf/$f"; then
    echo "IDENTICAL $f"
  else
    echo "DIFFERS $f"
    cmp "tests/vectors/$f" "$ROOT/scratch/verifier-w2xf/regen/xf/$f" | head -5
  fi
done
