#!/usr/bin/env bash
B=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32/berkeley/vecs
for m in te tz tp tn ta; do
  n=$(grep '^FAIL' "$B/f32_div-$m-l1.verify.log" | awk '{split($4,a,"/"); split($6,b,"/"); if (a[1]==b[1]) c++} END {print c+0}')
  echo "div-$m flag-only-bits-match: $n"
done
echo "=== div0-flag-only sample lines ==="
grep '^FAIL' "$B/f32_div-te-l1.verify.log" | awk '{split($4,a,"/"); split($6,b,"/"); if (a[1]==b[1]) print}' | head -n 4
