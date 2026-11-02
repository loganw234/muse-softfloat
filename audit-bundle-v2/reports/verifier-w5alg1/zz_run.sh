#!/usr/bin/env bash
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
$PY -u scratch/verifier-w5alg1/zz_hello.py
echo "rc=$?"
