#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-minmax || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4minmax
mkdir -p build/gate-t2
echo "== payload-f16-exhaustive =="
time "$MSF_PYTHON" tests/gen_vectors_tier2.py payload-f16-exhaustive build/gate-t2/payload-f16-exhaustive.vec || exit 1
echo "== seeded =="
time "$MSF_PYTHON" tests/gen_vectors_tier2.py seeded build/gate-t2/seeded-f32f64.vec 12000 || exit 1
echo "== minmax-f16-sweep =="
time "$MSF_PYTHON" tests/gen_vectors_tier2.py minmax-f16-sweep build/gate-t2/minmax-f16-sweep.vec || exit 1
ls -l build/gate-t2/
for f in build/gate-t2/payload-f16-exhaustive.vec build/gate-t2/seeded-f32f64.vec build/gate-t2/minmax-f16-sweep.vec; do
  echo "== verify $f =="
  time build/smoke/msf_runner.exe verify "$f" > "$S/verify-$(basename "$f" .vec).log" 2>&1
  rc=$?
  echo "rc=$rc"
  grep -E '^(file|prov|total|VERDICT)' "$S/verify-$(basename "$f" .vec).log" || tail -20 "$S/verify-$(basename "$f" .vec).log"
  [ $rc -eq 0 ] || exit 1
done
echo GATE-GEN-VERIFY-PASS
