#!/usr/bin/env bash
# 06_run_compare.sh - run tolerance-halving and cap probes, then compare.
set -u
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
OUT="$VROOT/scratch/verifier-w4interval"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
bash "$OUT/06_mono_cap.sh"
"$MSF_PYTHON" "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4interval/06_compare.py"
