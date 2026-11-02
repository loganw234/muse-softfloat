#!/bin/bash
# Probe G: build cross-decision samples (own RNG + own .wc parse/rank).
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
cd "$ROOT" || exit 9
"$PY" scratch/verifier-w4trig/samplegen.py scratch/verifier-w4trig/tmp/xdec.in
echo "rc=$?"
wc -l scratch/verifier-w4trig/tmp/xdec.in
