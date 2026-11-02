#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
echo "=== adv-dec FAILs NOT snan-related:"
grep '^FAIL adv/vw-adv-dec.vec' adv.log | grep -vi 'snan' | head -20
echo "=== count snan FAILs in adv-dec:"
grep '^FAIL adv/vw-adv-dec.vec' adv.log | grep -ci 'snan'
echo "=== adv-hex FAILs on inputs WITHOUT frac digits (not the x2 bug):"
grep '^FAIL adv/vw-adv-hex.vec' adv.log | grep -v 'IN=.*\.' | head -20
echo "=== adv-todec FAILs:"
grep '^FAIL adv/vw-adv-todec.vec' adv.log | head -10
echo "=== adv-tohex FAILs:"
grep '^FAIL adv/vw-adv-tohex.vec' adv.log | head -30
echo "=== malformed lines in adv-hex vec:"
grep -n ' ' adv/vw-adv-hex.vec | awk -F: '{print $1}' | head -30
