#!/usr/bin/env bash
# 12c_check.sh - inspect committed f64 +0 lines.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
grep -h "msf64_r_sqrt t. 0 ->" worktrees/verify5-alg1/tests/vectors/alg-f64.vec | head -8
echo ---
grep -h "msf32_r_sqrt t. 0 ->" worktrees/verify5-alg1/tests/vectors/alg-f32.vec | head -8
