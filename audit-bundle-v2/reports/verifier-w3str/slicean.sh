#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
echo "=== total fails: $(grep -c '^FAIL' slice.log)"
echo "=== snan fails: $(grep '^FAIL' slice.log | grep -ci 'snan')"
echo "=== from-hex with frac-digit input: $(grep '^FAIL' slice.log | grep -c 'from_hex.*IN=.*\.')"
echo "=== to-dec tie-pattern (2$ vs 3$ at digit end):"
grep '^FAIL' slice.log | grep -c 'to_decimal.*got OUT=.*3e.[0-9-]* want OUT=.*2e'
echo "=== any other fails:"
grep '^FAIL' slice.log | grep -vi 'snan' | grep -v 'from_hex.*IN=.*\.' | grep -v 'to_decimal.*got OUT=.*3e.[0-9-]* want OUT=.*2e' | head -20
