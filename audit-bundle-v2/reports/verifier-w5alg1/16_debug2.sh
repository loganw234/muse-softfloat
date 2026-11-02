#!/usr/bin/env bash
# 16_debug2.sh - reproduce the python capture path minimally.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
head -3 scratch/verifier-w5alg1/out/mpx_f16.txt
scratch/verifier-w5alg1/out/mpfrx.exe < scratch/verifier-w5alg1/out/mpx_f16.txt | head -3
echo "rc=$?"
