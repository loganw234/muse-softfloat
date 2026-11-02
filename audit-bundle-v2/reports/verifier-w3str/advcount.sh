#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
F=adv-fails.txt
grep '^FAIL' adv.log > $F
echo "total: $(wc -l < $F)"
echo "snan-consumed class: $(grep -ci 'snan' $F)"
echo "dec-tie class (to-dec + beyondh exact-half):"
grep '^FAIL' $F | grep -vi 'snan' | grep -vc 'from_hex'
grep '^FAIL' $F | grep -vi 'snan' | grep -v 'from_hex' | cut -c1-140
