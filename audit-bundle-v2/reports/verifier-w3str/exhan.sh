#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
echo "=== all 4516 fails match the te-tie pattern (got odd last digit, want even)?"
grep '^FAIL' exh.log | grep -vc 'got OUT=.*[0-9]3e.\?[+-]\?[0-9]* want OUT=.*[0-9]2e'
echo "above = non-tie-pattern fails (expect 0)"
echo "=== fails by SPEC:"
grep '^FAIL' exh.log | grep -o 'SPEC=[0-9]*' | sort | uniq -c
echo "=== fixed-runner fails: $(grep -c '^FAIL' fixed/exh.log)"
