#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
F=fuzz/fuzz.log
echo "=== the 127 non-snan non-hex fails: all te mode?"
grep '^FAIL' $F | grep -vi 'snan' | grep -v 'from_hex' | grep -vc ' te '
echo "above = non-te in bucket (expect 0)"
echo "=== from-dec ones: all >20 sig digits (beyond-H)?"
grep '^FAIL' $F | grep 'from_decimal' | grep -vi 'snan' | head -5 | cut -c1-150
echo "=== to-dec ones: tie pattern sample:"
grep '^FAIL' $F | grep 'to_decimal' | head -5 | cut -c1-160
echo "=== to-hex fails (expect 0):"
grep -c '^FAIL.*to_hex' $F
