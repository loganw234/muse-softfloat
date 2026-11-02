#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/scratch/verifier-w3str" || exit 9
SF=$R/scratch/verifier-w3str/sf.txt
grep '^FAIL' slice.log > $SF
echo "total: $(wc -l < $SF)"
echo "--- snan lines:"
grep -ci 'snan' $SF
grep -i 'snan' $SF | cut -c1-120
echo "--- non-snan from_hex lines:"
grep '^FAIL' $SF | grep -vi 'snan' | grep -c 'from_hex'
grep '^FAIL' $SF | grep -vi 'snan' | grep 'from_hex' | grep -vc 'IN=[^ ]*\. '
echo "above = from_hex fails WITHOUT frac digits (should be 0)"
echo "--- non-snan non-hexfrac lines:"
grep '^FAIL' $SF | grep -vi 'snan' | grep -v 'from_hex.*IN=[^ ]*\. ' | cut -c1-160
