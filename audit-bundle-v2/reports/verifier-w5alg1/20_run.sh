#!/usr/bin/env bash
# 20_run.sh - exact-case census (f16 exhaustive in decider; f32/f64 sampled).
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
ulimit -v 4194304
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe -u scratch/verifier-w5alg1/20_exactcount.py
