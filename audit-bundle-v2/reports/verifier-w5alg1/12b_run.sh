#!/usr/bin/env bash
# 12b_run.sh - my decider vs committed vectors.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe -u scratch/verifier-w5alg1/12b_vectors_vs_mine.py
