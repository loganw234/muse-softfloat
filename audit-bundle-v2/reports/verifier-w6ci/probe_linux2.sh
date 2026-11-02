#!/bin/sh
DUP=/mnt/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6ci/dup
VEC=$DUP/tests/vectors/encodings-f32.vec
OUT=/mnt/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6ci
awk 'BEGIN{d=0} {t=$NF; if (substr(t,length(t))=="\r") t=substr(t,1,length(t)-1)} /^msf32_class/ && !d && t=="exact-py:directed-encodings" {for(i=1;i<=NF;i++) if($i=="->" && ($(i+1)=="0"||$(i+1)=="1")) {$(i+1)=($(i+1)=="0"?"1":"0"); d=1}} {print}' "$VEC" > "$OUT/fixed-nanpol.vec"
cmp "$VEC" "$OUT/fixed-nanpol.vec"
echo "differing-bytes=$(cmp -l "$VEC" "$OUT/fixed-nanpol.vec" | wc -l)"
cmp -l "$VEC" "$OUT/fixed-nanpol.vec" | head -3
grep -c "$(printf '\r$')" "$OUT/fixed-nanpol.vec"
echo "== fixed tag stage =="
awk '!/^#/ && NF>0 {t=$NF; if (substr(t,length(t))=="\r") t=substr(t,1,length(t)-1); print t}' "$DUP"/tests/vectors/*.vec 2>/dev/null | sort | uniq -c | awk '{print $2, $1}' > "$OUT/fixed-expect.txt"
echo "FIXED tag lines carrying CR: $(grep -c "$(printf '\r')" "$OUT/fixed-expect.txt")"
echo "== inventory re-derivation =="
grep -c . "$DUP/docs/COVERAGE.tsv" | head -1
awk -F '\t' '!/^#/ && NR>1 {print $13, $9}' "$DUP/docs/COVERAGE.tsv" | sort | uniq -c
