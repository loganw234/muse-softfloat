#!/usr/bin/env bash
# 18b_run.sh - boundary probe vs own arithmetic.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe -u scratch/verifier-w5alg1/18_boundary.py
