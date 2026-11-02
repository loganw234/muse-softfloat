#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$R/scratch/verifier-w3str/tmp
export TMP="C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w3str\tmp"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
echo "=== regular runner on f16 exhaustive:"
./runner.exe verify exh/vw-exh-todec.vec exh/vw-exh-tohex.vec > exh.log 2>&1
echo "exit=$?"
grep -E '^(file|total|VERDICT)' exh.log
grep '^FAIL' exh.log | head -12
echo "=== fixed runner on f16 exhaustive:"
./fixed/runner-fixed.exe verify exh/vw-exh-todec.vec exh/vw-exh-tohex.vec > fixed/exh.log 2>&1
echo "exit=$?"
grep -E '^(file|total|VERDICT)' fixed/exh.log
