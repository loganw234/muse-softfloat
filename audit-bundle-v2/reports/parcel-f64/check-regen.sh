#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export TMPDIR=$PWD/build/w1/tmp
PY=../../.venv/Scripts/python.exe
rm -rf build/w1/regen-check
$PY tests/gen_vectors_f64.py directed build/w1/regen-check > build/w1/logs/regen-check.log 2>&1
echo "gen rc=$?"
for f in arith-f64.vec conv-f64.vec misc-f64.vec compare-f64.vec nan-f64.vec; do
  if cmp -s "tests/vectors/$f" "build/w1/regen-check/$f"; then echo "identical $f"; else echo "DIFF $f"; fi
done
sha256sum tests/vectors/arith-f64.vec tests/vectors/conv-f64.vec tests/vectors/misc-f64.vec tests/vectors/compare-f64.vec tests/vectors/nan-f64.vec > build/w1/logs/directed-sha256.txt
cat build/w1/logs/directed-sha256.txt
