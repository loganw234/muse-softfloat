#!/usr/bin/env bash
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32
cd "$S" || exit 9
for fam in xarith xarith-hom zeros; do
  echo "===== $fam ====="
  grep '^FAIL' "p3-verify-p3-$fam.log" | sed 's/.*| //' | awk '{print $1}' | sort | uniq -c | sort -rn
done
echo "===== xarith non-div/sub fails (if any) ====="
grep '^FAIL' p3-verify-p3-xarith.log | grep -v 'msf32_div' | grep -v 'msf32_sub' | head -n 10
echo "===== xarith-hom non-div/sub fails (if any) ====="
grep '^FAIL' p3-verify-p3-xarith-hom.log | grep -v 'msf32_div' | grep -v 'msf32_sub' | head -n 10
echo "===== zeros non-sub fails (if any) ====="
grep '^FAIL' p3-verify-p3-zeros.log | grep -v 'msf32_sub' | head -n 10
