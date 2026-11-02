#!/bin/bash
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT" || exit 9
diff worktrees/verify4-trig/tests/vectors/trig-f64.vec scratch/verifier-w4trig/tmp/vecregen/trig-f64.vec
echo "bash-diff rc=$?"
