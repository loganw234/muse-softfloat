#!/usr/bin/env bash
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32
cd "$S" || exit 9
echo "=== sub_f32_f64: non-inf fails (expect 0) ==="
grep '^FAIL' p3-verify-p3-xarith.log | grep 'msf32_sub_f32_f64' | grep -vc '7ff0000000000000\|fff0000000000000'
echo "=== sub_f32_f64 distinct shapes ==="
grep '^FAIL' p3-verify-p3-xarith.log | grep 'msf32_sub_f32_f64' | sed 's/.*| //' | awk '{print $4, $6}' | sort | uniq -c | head
echo "=== xarith div: NaN-involved fails (expect only exact-match nan lines pass; list any FAIL with nan input) ==="
grep '^FAIL' p3-verify-p3-xarith.log | grep 'msf32_div' | grep -c '7ff8\|fff8\|7ff0\|fff0\|7fc\|ffc\|7f8\|ff8'
echo "=== xarith div got/want flag combos ==="
grep '^FAIL' p3-verify-p3-xarith.log | grep 'msf32_div' | sed 's/.*got \([0-9a-f]*\)\/\([0-9a-f]*\) want \([0-9a-f]*\)\/\([0-9a-f]*\).*/\2 \4/' | sort | uniq -c | sort -rn | head -n 12
