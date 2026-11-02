#!/usr/bin/env bash
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32
cd "$S" || exit 9
for fam in fromint logb nanmat remainder toint zeros; do
  echo "===== $fam ====="
  grep '^FAIL' "p3-verify-p3-$fam.log" | head -n 6
done
