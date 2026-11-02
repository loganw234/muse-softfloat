#!/usr/bin/env bash
set -uo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/parcel-xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-xf\tmp'
export TEMP="$TMP"
cd "$ROOT/worktrees/w2-xf" || exit 9
PY="$ROOT/.venv/Scripts/python.exe"
echo "== second sweeps =="
"$PY" tests/gen_vectors_xf.py sweep build/w2/sweep2-f32.vec 315000 555 f32
"$PY" tests/gen_vectors_xf.py sweep build/w2/sweep2-f64.vec 315000 556 f64
./build/w2/msf_runner.exe verify build/w2/sweep2-f32.vec build/w2/sweep2-f64.vec > build/w2/verify-sweeps2.log 2>&1
echo "verify sweeps2 exit=$?"
grep -E '^(prov|total|VERDICT)' build/w2/verify-sweeps2.log
echo "== neighbor audit (sampled every 37th line) =="
"$PY" "$ROOT/scratch/parcel-xf/scripts/17_neighbor_audit.py" \
  build/w2/sweep-f32.vec build/w2/sweep-f64.vec \
  build/w2/sweep2-f32.vec build/w2/sweep2-f64.vec \
  tests/vectors/arith-xf.vec tests/vectors/fma-sqrt-xf.vec tests/vectors/conv-xf.vec \
  > build/w2/neighbor-audit.log 2>&1
echo "audit exit=$?"
cat build/w2/neighbor-audit.log
echo "== directed regeneration stability =="
mkdir -p "$ROOT/scratch/parcel-xf/regen-check"
"$PY" tests/gen_vectors_xf.py directed "$ROOT/scratch/parcel-xf/regen-check" > build/w2/regen-check.log 2>&1
echo "regen gen exit=$?"
ok=1
for f in arith-xf.vec fma-sqrt-xf.vec conv-xf.vec compare-xf.vec traps-xf.vec; do
  if cmp -s "tests/vectors/$f" "$ROOT/scratch/parcel-xf/regen-check/$f"; then
    echo "regen $f: byte-identical"
  else
    echo "regen $f: DIFFERS"; ok=0
  fi
done
echo "regen stability ok=$ok"
