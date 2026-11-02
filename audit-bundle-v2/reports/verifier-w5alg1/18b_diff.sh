#!/usr/bin/env bash
# 18b_diff.sh - show regen-vs-committed diff for alg-f64.vec.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
diff worktrees/verify5-alg1/tests/vectors/alg-f64.vec scratch/verifier-w5alg1/out/alg1/alg-f64.vec
echo "diff rc=$?"
