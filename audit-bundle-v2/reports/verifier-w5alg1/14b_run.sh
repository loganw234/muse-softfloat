#!/usr/bin/env bash
# 14b_run.sh - sign-split breakdown of the volume mismatches.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe -u scratch/verifier-w5alg1/14b_signsplit.py
