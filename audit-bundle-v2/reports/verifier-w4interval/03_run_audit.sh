#!/usr/bin/env bash
# 03_run_audit.sh - run the independent containment audit.
set -u
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
OUT="$VROOT/scratch/verifier-w4interval"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
"$MSF_PYTHON" "$OUT/03_audit.py" 2>&1 | tee "$OUT/build/audit.txt"
