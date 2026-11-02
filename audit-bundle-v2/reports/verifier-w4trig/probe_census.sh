#!/bin/bash
# Probe U: table-index bounds, provenance-tag census of committed vectors,
# NTERMS vs table sizes.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
V=$ROOT/scratch/verifier-w4trig
C=$ROOT/worktrees/verify4-trig
cd "$ROOT" || exit 9
echo "=== header dims ==="
grep -nE 'NSIN|NCOS|NTERMS|STAGE_LIMBS' $C/src/msf_trig_tables.h
echo "=== kernel max index use ==="
grep -n 'SIN_C\[\|COS_C\[' $C/src/msf_math.c | head
echo "=== vector provenance census ==="
cat $C/tests/vectors/trig-f16.vec $C/tests/vectors/trig-f32.vec $C/tests/vectors/trig-f64.vec | awk '{print $NF}' | sort | uniq -c | sort -rn
echo "=== vector op/mode census ==="
cat $C/tests/vectors/trig-f16.vec $C/tests/vectors/trig-f32.vec $C/tests/vectors/trig-f64.vec | awk '{print $1, $2}' | sort | uniq -c | sort -rn | head -30
