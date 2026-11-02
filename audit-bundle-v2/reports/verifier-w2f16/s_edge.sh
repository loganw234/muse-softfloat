#!/usr/bin/env bash
# s_edge.sh - replay probe-5 edge vectors
set -u
cd "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16" || exit 9
SC="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
R="build/smoke/msf_runner.exe"
C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe "$SC/gen_edge.py"
"$R" verify "$SC/edge-exact.vec" > "$SC/edge-exact.log" 2>&1
echo "exact: $(grep -E '^(total|VERDICT)' "$SC/edge-exact.log" | tr '\n' ' ')"
grep -E '^FAIL' "$SC/edge-exact.log" | head -30
"$R" verify "$SC/edge-nanclass.vec" > "$SC/edge-nanclass.log" 2>&1
echo "nanclass: $(grep -E '^(total|VERDICT)' "$SC/edge-nanclass.log" | tr '\n' ' ')"
grep -E '^FAIL' "$SC/edge-nanclass.log" | head -30
