#!/bin/bash
# Probe A (rerun): regenerate trig tables to scratch tmp and byte-compare.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
cd "$ROOT" || exit 9
mkdir -p scratch/verifier-w4trig/tmp
"$PY" worktrees/verify4-trig/tools/gen_trig_tables.py scratch/verifier-w4trig/tmp/trig-regen.h > scratch/verifier-w4trig/log_regen.txt 2>&1
echo "gen rc=$?"
cat scratch/verifier-w4trig/log_regen.txt
cmp -l worktrees/verify4-trig/src/msf_trig_tables.h scratch/verifier-w4trig/tmp/trig-regen.h | head -20
echo "cmp rc=$? (0 means byte-identical)"
