#!/usr/bin/env bash
set -uo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/parcel-xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-xf\tmp'
export TEMP="$TMP"
cd "$ROOT/worktrees/w2-xf" || exit 9
PY="$ROOT/.venv/Scripts/python.exe"
mkdir -p build/w2
echo "== sweep f32 315000 seed 20261027 =="
time "$PY" tests/gen_vectors_xf.py sweep build/w2/sweep-f32.vec 315000 20261027 f32
echo "gen exit=$?"
echo "== sweep f64 315000 seed 777001 =="
time "$PY" tests/gen_vectors_xf.py sweep build/w2/sweep-f64.vec 315000 777001 f64
echo "gen exit=$?"
echo "== exhaustive f16 unary =="
time "$PY" tests/gen_vectors_xf.py exhaustive-f16 build/w2/exhaustive-f16-xf.vec
echo "gen exit=$?"
echo "== replay sweeps =="
time ./build/w2/msf_runner.exe verify build/w2/sweep-f32.vec build/w2/sweep-f64.vec > build/w2/verify-sweeps.log 2>&1
echo "verify sweeps exit=$?"
tail -8 build/w2/verify-sweeps.log
echo "== replay exhaustive =="
time ./build/w2/msf_runner.exe verify build/w2/exhaustive-f16-xf.vec > build/w2/verify-exhaustive.log 2>&1
echo "verify exhaustive exit=$?"
tail -8 build/w2/verify-exhaustive.log
