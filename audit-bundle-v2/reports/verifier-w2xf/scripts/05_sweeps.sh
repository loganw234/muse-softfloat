#!/usr/bin/env bash
# 05_sweeps.sh - verify independent sweeps with the copy runner; build mutants
set -uo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/verifier-w2xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w2xf\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$ROOT/worktrees/verify2-xf" || exit 9
VX="$ROOT/scratch/verifier-w2xf"
echo "== sweep verify =="
./build/smoke/msf_runner.exe verify "$VX/sweeps/sweep-f32-101.vec" "$VX/sweeps/sweep-f32-202.vec" \
  "$VX/sweeps/sweep-f64-303.vec" "$VX/sweeps/sweep-f64-404.vec" > "$VX/sweep-verify.log" 2>&1
echo "verify exit=$?"
grep -E "^(file|total|VERDICT)" "$VX/sweep-verify.log"
grep -c "^FAIL" "$VX/sweep-verify.log" || true
