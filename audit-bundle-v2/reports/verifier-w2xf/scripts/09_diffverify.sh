#!/usr/bin/env bash
# 09_diffverify.sh - verify own differential vectors with the copy runner
set -uo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/verifier-w2xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w2xf\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$ROOT/worktrees/verify2-xf" || exit 9
VX="$ROOT/scratch/verifier-w2xf"
./build/smoke/msf_runner.exe verify "$VX/berkeley-diff/diff-f32.vec" > "$VX/diff-verify-f32.log" 2>&1
echo "f32 exit=$? : $(grep -E '^(total|VERDICT)' "$VX/diff-verify-f32.log" | tr '\n' ' ')"
./build/smoke/msf_runner.exe verify "$VX/berkeley-diff/diff-f64.vec" > "$VX/diff-verify-f64.log" 2>&1
echo "f64 exit=$? : $(grep -E '^(total|VERDICT)' "$VX/diff-verify-f64.log" | tr '\n' ' ')"
