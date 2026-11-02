#!/usr/bin/env bash
B=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32/berkeley/vecs
for m in te tz tp tn ta; do
  n=$(grep '^FAIL' "$B/f32_div-$m-l1.verify.log" | awk '{split($4,a,"/"); split($6,b,"/"); if (("x" a[1])==("x" b[1])) c++} END {print c+0}')
  echo "div-$m flag-only-bits-match: $n"
done
echo "=== flag-only distinct want-flags shapes ==="
grep '^FAIL' "$B/f32_div-te-l1.verify.log" | awk '{split($4,a,"/"); split($6,b,"/"); if (("x" a[1])==("x" b[1])) print "gotflags="a[2] " wantflags="b[2]}' | sort | uniq -c
