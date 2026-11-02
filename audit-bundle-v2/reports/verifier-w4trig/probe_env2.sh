#!/bin/bash
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
P=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
$P scratch/verifier-w4trig/pyinfo.py
echo "rc=$?"
