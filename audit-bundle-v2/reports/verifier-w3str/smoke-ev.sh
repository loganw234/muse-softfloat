#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
echo "=== smoke.log (budget outcome in the copy):"
cat smoke.log
echo
echo "=== control-9 probe detail:"
./runner.exe verify planned.vec 2>&1 | head -20
