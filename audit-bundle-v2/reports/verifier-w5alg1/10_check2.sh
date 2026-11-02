#!/usr/bin/env bash
# 10_check2.sh - compare my decider rsqrt(2.0) f64 vs committed vector.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
grep -h "msf64_r_sqrt te 4000000000000000" worktrees/verify5-alg1/tests/vectors/alg-f64.vec
grep -h "msf32_r_sqrt te 40000000" worktrees/verify5-alg1/tests/vectors/alg-f32.vec
grep -h "msf16_r_sqrt te 4000" worktrees/verify5-alg1/tests/vectors/alg-f16.vec
