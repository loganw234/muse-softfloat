#!/usr/bin/env bash
# Tamper experiments (a),(c)-(g): vector-file tampering against the smoke gate's vector step, reproduced by hand.
SP=/tmp/claude-0/-home-user-muse-softfloat/f663923d-ec02-5a9b-9be5-2326751bedd2/scratchpad
A=$SP/agents/test-infra
source $A/scripts/lib.sh
R=$A/build/msf_runner.exe
W=$A/tamper; rm -rf $W; mkdir -p $W
fresh() { rm -rf $W/work; mkdir -p $W/work; cp -r $A/repo/{src,include,tests,tools} $W/work/; }
run() { # label, then gate_verify in $W/work
  local label="$1"; local out; out=$(gate_verify $W/work $R $W/out-$(echo "$label" | tr ' /' '__') 2>&1 | tail -1)
  printf '%-62s %s\n' "$label" "$out"; }
fresh; run "00 baseline (untouched)"
V=tests/vectors
# (a) delete 90% of a big file's lines (keep header comments + every 10th vector)
fresh; awk 'FNR<=3 || /^#/ {print; next} (++n % 10)==0 {print}' $W/work/$V/aug-f64.vec > $W/x && mv $W/x $W/work/$V/aug-f64.vec; run "(a1) aug-f64.vec: keep 10% of lines"
fresh; : > $W/work/$V/trig-f64.vec; run "(a2) trig-f64.vec: emptied to 0 bytes"
fresh; head -3 $V/../vectors/trig-f64.vec 2>/dev/null >/dev/null; head -3 $A/repo/$V/trig-f64.vec > $W/work/$V/trig-f64.vec; run "(a3) trig-f64.vec: header comments only (22,610 vectors removed)"
fresh; rm $W/work/$V/explog-f64.vec; run "(a4) explog-f64.vec: file deleted (still listed in VECS)"
# (c) truncate mid-line
fresh; f=$W/work/$V/arith-f32.vec; sz=$(stat -c %s $f); head -c $((sz-60)) $f > $W/x && mv $W/x $f; run "(c1) arith-f32.vec: truncated 60 bytes (mid result/flags field)"
fresh; f=$W/work/$V/arith-f32.vec; sz=$(stat -c %s $f); head -c $((sz-8)) $f > $W/x && mv $W/x $f; tail -c 80 $f | od -c | tail -3 | head -2 >/dev/null; run "(c2) arith-f32.vec: truncated 8 bytes (inside last provenance tag, no final newline)"
fresh; f=$W/work/$V/arith-f32.vec; sz=$(stat -c %s $f); head -c $((sz-1)) $f > $W/x && mv $W/x $f; run "(c3) arith-f32.vec: final newline removed only"
# (d) unknown function name / commented-out / extra-token lines
fresh; echo "msf32_frobnicate te 3f800000 3f800000 -> 40000000 00 exact-py:fake" >> $W/work/$V/arith-f32.vec; run "(d1) append line with unknown op name"
fresh; sed -i '10s/^/#/' $W/work/$V/arith-f32.vec; run "(d2) comment out one vector (prefix '#')"
fresh; sed -i '10,4000s/^/#/' $W/work/$V/arith-f32.vec; run "(d3) comment out vector lines 10-4000 of arith-f32.vec"
fresh; echo "msf32_add te 3f800000 3f800000 -> 40000000 00 exact-py:fake extra1 extra2" >> $W/work/$V/arith-f32.vec; run "(d4) known op, extra trailing tokens"
fresh; echo "msf32_add te 3f800000 3f800000 -> 40000000 00 totally-new-provenance-tag" >> $W/work/$V/arith-f32.vec; run "(d5) valid new line with brand-new provenance tag"
fresh; echo "msf32_add te 3f800000 3f800000 -> zzzz 00 exact-py:fake" >> $W/work/$V/arith-f32.vec; run "(d6) hex field garbage in expected result (strtoull -> 0)"
# (e) duplicates
fresh; f=$W/work/$V/aug-f32.vec; cat $f >> $W/x; cat $f >> $W/x; mv $W/x $f; run "(e1) aug-f32.vec: whole content duplicated twice"
fresh; f=$W/work/$V/arith-f32.vec; awk '!/^#/ {for(i=0;i<50;i++) print; next} {print}' $f > $W/x && mv $W/x $f; run "(e2) arith-f32.vec: each vector repeated 50x"
# (f) CRLF/LF variants
fresh; for g in $W/work/$V/arith-f32.vec; do sed -i 's/$/\r/' $g; done; run "(f1) arith-f32.vec LF -> CRLF"
fresh; sed -i 's/\r$//' $W/work/$V/pack64.vec; run "(f2) pack64.vec CRLF -> LF"
fresh; awk 'NR%2==0 {printf "%s\r\n",$0; next} {print}' $W/work/$V/arith-f32.vec > $W/x && mv $W/x $W/work/$V/arith-f32.vec; run "(f3) arith-f32.vec mixed CRLF/LF (every 2nd line)"
fresh; sed -i 's/$/\r\r/' $W/work/$V/arith-f32.vec; run "(f4) arith-f32.vec lines end CR CR LF"
# (g) masking directive injected
fresh; sed -i '1i # compare=nan-class' $W/work/$V/arith-f32.vec; run "(g1) '# compare=nan-class' injected at top of arith-f32.vec (no other change)"
fresh; sed -i '1i # compare=berkeley-int' $W/work/$V/toint-f32.vec; run "(g2) '# compare=berkeley-int' injected at top of toint-f32.vec"
