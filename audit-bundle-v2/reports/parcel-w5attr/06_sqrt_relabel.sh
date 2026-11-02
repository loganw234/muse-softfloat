#!/usr/bin/env bash
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-attr" || exit 9
S="$WS/scratch/parcel-w5attr"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
PY="$MSF_PYTHON"
R=build/smoke/msf_runner.exe
"$PY" "$S/make_sqrt_relabel.py" "$PWD" "$S/out/ctrl" > "$S/out/ctrl/sqrt_relabel_make.log" 2>&1
echo "make rc=$?"; cat "$S/out/ctrl/sqrt_relabel_make.log"
echo "===== homog+widening sqrt relabel (theorem scope, must PASS) ====="
"$R" verify "$S/out/ctrl/sqrt_relabel_theorem.vec" > "$S/out/ctrl/verify_sqrt_relabel_theorem.log" 2>&1
echo "verify rc=$?"
grep -E '^(total|VERDICT)' "$S/out/ctrl/verify_sqrt_relabel_theorem.log"
echo "===== full sqrt relabel (must FAIL exactly on narrowing ties) ====="
"$R" verify "$S/out/ctrl/sqrt_relabel_full.vec" > "$S/out/ctrl/verify_sqrt_relabel_full.log" 2>&1
echo "verify rc=$?"
grep -E '^(total|VERDICT)' "$S/out/ctrl/verify_sqrt_relabel_full.log"
grep '^FAIL' "$S/out/ctrl/verify_sqrt_relabel_full.log" | head -8 || true
