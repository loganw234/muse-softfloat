#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
$PY scratch/parcel-w4trig/pick_hardest.py > scratch/parcel-w4trig/out/hardest_ext.txt 2> scratch/parcel-w4trig/out/hardest_ext.err
echo "pick rc=$?"
$PY scratch/parcel-w4trig/splice_hardest.py
$PY scratch/parcel-w4trig/check_parse.py
grep -c "0x" worktrees/w4-trig/tests/gen_vectors_trig.py
