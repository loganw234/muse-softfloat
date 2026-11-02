#!/usr/bin/env bash
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32
cd "$S" || exit 9
echo "=== got14/want00 lines ==="
grep '^FAIL' p3-verify-p3-xarith.log | grep 'msf32_div' | awk '{split($4,a,"/"); split($6,b,"/"); if ((("x" a[2])==("x" "14")) && ((("x" b[2])==("x" "00")))) print}' | head -n 8
echo "=== div FAILs with a NaN INPUT operand ==="
grep '^FAIL' p3-verify-p3-xarith.log | grep 'msf32_div' | sed 's/.*| //' > /tmp/divf.txt
grep -iE 'msf32_div(_[a-z0-9]+)? [a-z]+ [0-9a-f]*[78]ff[08][0-9a-f]* ' /tmp/divf.txt | head -n 8
echo "=== count div FAILs by input class ==="
grep -c '^' /tmp/divf.txt
