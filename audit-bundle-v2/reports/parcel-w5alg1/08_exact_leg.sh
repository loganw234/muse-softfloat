#!/usr/bin/env bash
# 08_exact_leg.sh - independent exact-Python exhaustive leg for
# binary16 through the real runner (decider-free second oracle).
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg1" || exit 9
S="$WS/scratch/parcel-w5alg1"
mkdir -p "$S/out" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg1\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
PY="$MSF_PYTHON"
time "$PY" "$S/make_f16_exhaustive_exact.py" "$PWD" "$S/out/f16_exact_exhaustive.vec" \
  > "$S/out/f16_exact_gen.log" 2>&1; echo "gen rc=$?"
cat "$S/out/f16_exact_gen.log"
time "$S/out/ctrl/runner.exe" verify "$S/out/f16_exact_exhaustive.vec" \
  > "$S/out/f16_exact_verify.log" 2>&1; echo "verify rc=$?"
grep -E 'file|prov|total|VERDICT' "$S/out/f16_exact_verify.log"
echo "===== 08_exact_leg done ====="
