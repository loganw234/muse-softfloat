#!/usr/bin/env bash
# s_ta.sh - replay ta probe
set -u
cd "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16" || exit 9
SC="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe "$SC/gen_taprove.py"
build/smoke/msf_runner.exe verify "$SC/ta-probe.vec" > "$SC/ta-probe.log" 2>&1
grep -E '^(total|VERDICT)' "$SC/ta-probe.log"
grep -E '^FAIL' "$SC/ta-probe.log"
