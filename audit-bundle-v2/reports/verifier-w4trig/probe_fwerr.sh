#!/bin/bash
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT" || exit 9
grep -B2 -A12 'FAILED' scratch/verifier-w4trig/log_fwbuild.txt | head -60
