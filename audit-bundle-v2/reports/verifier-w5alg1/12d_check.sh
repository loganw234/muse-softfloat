#!/usr/bin/env bash
# 12d_check.sh - inspect committed signed-zero lines in all formats.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
V=worktrees/verify5-alg1/tests/vectors
grep -h "msf16_r_sqrt t. 0 ->" $V/alg-f16.vec
echo ---
grep -h "msf16_r_sqrt t. 8000 ->" $V/alg-f16.vec
echo ---
grep -h "msf32_r_sqrt t. 80000000 ->" $V/alg-f32.vec
echo ---
grep -h "msf64_r_sqrt t. 0 ->" $V/alg-f64.vec
echo ---
grep -h "msf64_r_sqrt t. 8000000000000000 ->" $V/alg-f64.vec
