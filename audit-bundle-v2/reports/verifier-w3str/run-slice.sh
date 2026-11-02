#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$R/scratch/verifier-w3str/tmp
export TMP="C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w3str\tmp"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
./runner.exe verify mpfrslice/vw-mpfr-slice.vec > slice.log 2>&1
echo "exit=$?"
grep -E '^(file|total|VERDICT)' slice.log
echo "=== fails not in known classes:"
grep '^FAIL' slice.log | grep -vi 'snan' | grep -v 'IN=.*\.' | head -20
