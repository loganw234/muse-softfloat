#!/usr/bin/env bash
# 06_resweep.sh - regenerate sweeps (compare rm fix) and verify
set -uo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/verifier-w2xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w2xf\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$ROOT" || exit 9
PY="$ROOT/.venv/Scripts/python.exe"
VX="$ROOT/scratch/verifier-w2xf"
"$PY" scratch/verifier-w2xf/scripts/03_indref.py sweep worktrees/verify2-xf "$VX/sweeps" 101 f32
"$PY" scratch/verifier-w2xf/scripts/03_indref.py sweep worktrees/verify2-xf "$VX/sweeps" 202 f32
"$PY" scratch/verifier-w2xf/scripts/03_indref.py sweep worktrees/verify2-xf "$VX/sweeps" 303 f64
"$PY" scratch/verifier-w2xf/scripts/03_indref.py sweep worktrees/verify2-xf "$VX/sweeps" 404 f64
cd "$ROOT/worktrees/verify2-xf" || exit 9
./build/smoke/msf_runner.exe verify "$VX/sweeps/sweep-f32-101.vec" "$VX/sweeps/sweep-f32-202.vec" \
  "$VX/sweeps/sweep-f64-303.vec" "$VX/sweeps/sweep-f64-404.vec" > "$VX/sweep-verify.log" 2>&1
echo "verify exit=$?"
grep -E "^(file|total|VERDICT)" "$VX/sweep-verify.log"
