#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export MSF_TRIG_DECIDER=$PWD/build/trig/trig_exhaustive.exe
$PY tests/gen_vectors_trig.py tests/vectors
echo "gen rc=$?"
wc -l tests/vectors/trig-*.vec
head -5 tests/vectors/trig-f16.vec
grep -h -o 'mpfr640-trig:[a-z]*' tests/vectors/trig-*.vec | sort | uniq -c
