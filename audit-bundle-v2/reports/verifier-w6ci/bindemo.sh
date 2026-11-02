#!/bin/bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6ci/dup || exit 9
VEC=tests/vectors/encodings-f32.vec
OUT=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6ci
export BINMODE=3
echo "awk=$(awk --version | head -1) BINMODE=$BINMODE"
echo "len(NF) line1024: $(awk 'NR==1024{print length($NF)}' "$VEC") (28=binary/Linux, 27=text)"
echo "== OLD =="
awk 'BEGIN{d=0} /^msf32_class/ && !d && $NF=="exact-py:directed-encodings" {for(i=1;i<=NF;i++) if($i=="->" && ($(i+1)=="0"||$(i+1)=="1")) {$(i+1)=($(i+1)=="0"?"1":"0"); d=1}} {print}' "$VEC" > "$OUT/bin-old.vec"
cmp -s "$VEC" "$OUT/bin-old.vec" && echo "OLD: 0 diff bytes (failure reproduced under binary mode)" || echo "OLD: differs"
echo "== NEW (committed fix) =="
awk 'BEGIN{d=0} {t=$NF; if (substr(t,length(t))=="\r") t=substr(t,1,length(t)-1)} /^msf32_class/ && !d && $NF=="exact-py:directed-encodings" {for(i=1;i<=NF;i++) if($i=="->" && ($(i+1)=="0"||$(i+1)=="1")) {$(i+1)=($(i+1)=="0"?"1":"0"); d=1}} {print}' "$VEC" > "$OUT/bin-new.vec"
cmp -s "$VEC" "$OUT/bin-new.vec" && echo "NEW: 0 diff bytes (fix is a no-op: still matches \$NF)" || echo "NEW: differs"
echo "== FIXED (compare stripped t) =="
awk 'BEGIN{d=0} {t=$NF; if (substr(t,length(t))=="\r") t=substr(t,1,length(t)-1)} /^msf32_class/ && !d && t=="exact-py:directed-encodings" {for(i=1;i<=NF;i++) if($i=="->" && ($(i+1)=="0"||$(i+1)=="1")) {$(i+1)=($(i+1)=="0"?"1":"0"); d=1}} {print}' "$VEC" > "$OUT/bin-fixed.vec"
cmp "$VEC" "$OUT/bin-fixed.vec" | head -2
cmp -l "$VEC" "$OUT/bin-fixed.vec" | wc -l
echo "== tag stage under binary mode =="
awk '!/^#/ && NF>0 {t=$NF; if (substr(t,length(t))=="\r") t=substr(t,1,length(t)-1); print $NF}' tests/vectors/*.vec 2>/dev/null | sort | uniq -c | awk '{print $2, $1}' > "$OUT/bin-new-expect.txt"
echo "NEW tag lines carrying CR: $(grep -c "$(printf '\r')" "$OUT/bin-new-expect.txt")"
