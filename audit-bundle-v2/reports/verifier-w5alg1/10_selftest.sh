#!/usr/bin/env bash
# 10_selftest.sh - smoke-test my own decider on known values.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
$PY -u scratch/verifier-w5alg1/10_selftest.py
