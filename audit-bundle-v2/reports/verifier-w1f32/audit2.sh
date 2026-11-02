#!/usr/bin/env bash
B=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32/berkeley/vecs
echo "=== sub-te: all FAIL lines involve an infinity operand? ==="
grep '^FAIL' "$B/f32_sub-te-l1.verify.log" | grep -vc '7f800000\|ff800000'
echo "=== sub-te: distinct got/want shapes ==="
grep '^FAIL' "$B/f32_sub-te-l1.verify.log" | sed 's/.*| //' | awk '{print $1, $4, $6}' | sort | uniq -c | head
echo "=== div-te: FAILs where result bits match (flag-only)? ==="
grep '^FAIL' "$B/f32_div-te-l1.verify.log" | awk '{split($3,a,"/"); split($5,b,"/"); if (a[1]==b[1]) print}' | wc -l
echo "=== div-te: flag-only distinct ==="
grep '^FAIL' "$B/f32_div-te-l1.verify.log" | awk '{split($3,a,"/"); split($5,b,"/"); if (a[1]==b[1]) print $0}' | head -n 4
echo "=== div-te: value-fail sample ==="
grep '^FAIL' "$B/f32_div-te-l1.verify.log" | head -n 3
