#!/usr/bin/env bash
# 16_debug.sh - run mpfrx on two lines directly.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
printf 'f16 3c00\nf16 1\n' | scratch/verifier-w5alg1/out/mpfrx.exe
echo "rc=$?"
