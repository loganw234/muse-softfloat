#!/bin/bash
# Probe N: regeneration byte-identity - (a) gen_tables.py 4 outputs,
# (b) trig vectors via committed generator + vehicle decider.
# (c) hand-written line ceiling count.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
V=$ROOT/scratch/verifier-w4trig
C=$ROOT/worktrees/verify4-trig
cd "$ROOT" || exit 9
echo "=== (a) gen_tables drift ==="
rm -rf $V/tmp/gen-check
"$PY" $C/tools/gen_tables.py $V/tmp/gen-check > $V/log_gentables.txt 2>&1
echo "gen rc=$?"
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  if cmp -s $C/$f $V/tmp/gen-check/$f; then echo "IDENTICAL $f"; else echo "DRIFT $f"; fi
done
echo "=== (b) trig vectors regen ==="
mkdir -p $V/tmp/vecregen
MSF_TRIG_DECIDER=$V/tmp/trigx.exe "$PY" $C/tests/gen_vectors_trig.py $V/tmp/vecregen > $V/log_vecregen.txt 2>&1
echo "vecgen rc=$?"
cat $V/log_vecregen.txt | head -5
for f in trig-f16 trig-f32 trig-f64; do
  if cmp -s $C/tests/vectors/$f.vec $V/tmp/vecregen/$f.vec; then echo "IDENTICAL $f.vec"; else echo "DRIFT $f.vec"; fi
done
wc -l $C/tests/vectors/trig-f16.vec $C/tests/vectors/trig-f32.vec $C/tests/vectors/trig-f64.vec
echo "=== (c) hand-written line count ==="
wc -l $C/src/msf_math.c $C/tools/gen_trig_tables.py $C/tests/gen_vectors_trig.py $C/tests/trig_exhaustive.c
