#!/bin/bash
# Probe E: run independent floor + Ek checks.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
cd "$ROOT" || exit 9
echo "=== floors ==="
"$PY" scratch/verifier-w4trig/check_floors.py
echo "floors rc=$?"
echo "=== Ek ==="
"$PY" scratch/verifier-w4trig/check_ek.py
echo "ek rc=$?"
