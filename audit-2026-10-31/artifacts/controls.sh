#!/usr/bin/env bash
# Re-run the P0 negative controls of tools/run.sh (lines 213-280) by hand and print WHY each is refused.
SP=/tmp/claude-0/-home-user-muse-softfloat/f663923d-ec02-5a9b-9be5-2326751bedd2/scratchpad
A=$SP/agents/test-infra
source $A/scripts/lib.sh
cd $A/repo
R=$A/build/msf_runner.exe
C=$A/ctrl; rm -rf $C; mkdir -p $C
BUILD=$C/b; mkdir -p $BUILD
write_manifest "$BUILD/manifest.txt" $SRC tests/runner.c tests/sha256.c include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h $VECS
write_expect_counts "$BUILD/expect.txt" $VECS
why() { # name rc logfile : summarise
  local n="$1" rc="$2" lg="$3"
  echo "[$n] rc=$rc | $(grep -E '^total' $lg | tr -s ' ') | $(grep -E '^VERDICT' $lg) | FAIL-lines=$(grep -c '^FAIL' $lg) malformed-FAIL-lines=$(grep -c '^FAIL.*\(malformed\|shape\|unknown op\|mismatch\)' $lg) | $(grep -E 'MISMATCH|COUNT' $lg | head -1)"
  grep -m2 '^FAIL' $lg | cut -c1-230
}
# 1
awk 'BEGIN{d=0} /^msf16_is_signaling/ && !d {for(i=1;i<=NF;i++) if($i=="->") $(i+1)=($(i+1)=="1"?"0":"1"); d=1} {print}' tests/vectors/encodings-f16.vec > $C/corrupt.vec
$R verify $C/corrupt.vec > $C/corrupt.log 2>&1; why "1 corrupted-expected-bit" $? $C/corrupt.log
echo "     changed lines vs original: $(diff <(tr -d '\r' < tests/vectors/encodings-f16.vec) <(tr -d '\r' < $C/corrupt.vec) | grep -c '^<')"
# 2
awk 'BEGIN{d=0} {t=$NF; if (substr(t,length(t))=="\r") t=substr(t,1,length(t)-1)} /^msf32_class/ && !d && t=="exact-py:directed-encodings" {for(i=1;i<=NF;i++) if($i=="->" && ($(i+1)=="0"||$(i+1)=="1")) {$(i+1)=($(i+1)=="0"?"1":"0"); d=1}} {print}' tests/vectors/encodings-f32.vec > $C/nanpol.vec
$R verify $C/nanpol.vec > $C/nanpol.log 2>&1; why "2 wrong-nan-expectation" $? $C/nanpol.log
echo "     changed lines vs original: $(diff <(tr -d '\r' < tests/vectors/encodings-f32.vec) <(tr -d '\r' < $C/nanpol.vec) | grep -c '^<')  (control 2 grep requires only rc!=0)"
# 3
awk '{if($1=="internal.pack64"){if($2=="te")$2="tz"; else if($2=="tz")$2="te"} print}' tests/vectors/pack64.vec > $C/wrongrm.vec
$R verify $C/wrongrm.vec > $C/wrongrm.log 2>&1; why "3 wrong-rounding-mode(pack64 te<->tz)" $? $C/wrongrm.log
# 3b
awk '{if($2=="te")$2="ta"; else if($2=="ta")$2="te"} {print}' tests/vectors/arith-f32.vec > $C/wrongrm-ta.vec
$R verify $C/wrongrm-ta.vec > $C/wrongrm-ta.log 2>&1; why "3b wrong-rounding-mode-te-ta (arith-f32)" $? $C/wrongrm-ta.log
# 4
awk 'BEGIN{d=0} $1=="internal.pack64" && !d && $(NF-1)!="00" {$(NF-1)="00"; d=1} {print}' tests/vectors/pack64.vec > $C/wrongflag.vec
$R verify $C/wrongflag.vec > $C/wrongflag.log 2>&1; why "4 wrong-flag-bit" $? $C/wrongflag.log
echo "     changed lines vs original: $(diff <(tr -d '\r' < tests/vectors/pack64.vec) <(tr -d '\r' < $C/wrongflag.vec) | grep -c '^<')"
# 5
sed '1s/^./0/' "$BUILD/manifest.txt" > "$C/bad-manifest.txt"
echo "     manifest line1 first char originally: '$(head -c1 $BUILD/manifest.txt)'  (control is a no-op if this is 0)"
$R verify --manifest "$C/bad-manifest.txt" tests/vectors/encodings-f16.vec > "$C/manifest.log" 2>&1; echo "[5 stale-manifest] rc=$? $(grep -E 'MANIFEST' $C/manifest.log | cut -c1-150)"
# 6
awk '{if(NR==1) $2=$2+1; print}' "$BUILD/expect.txt" > "$C/bad-expect.txt"
$R verify --expect-counts "$C/bad-expect.txt" tests/vectors/encodings-f16.vec > "$C/count.log" 2>&1; echo "[6 count-mismatch] rc=$? $(grep -E 'COUNT MISMATCH' $C/count.log | cut -c1-150) | total line: $(grep ^total $C/count.log)"
echo "     expect.txt first line: $(head -1 $BUILD/expect.txt)  (first tag in file order after sort)"
# 7
gcc $CFLAGS -DMSF_TININESS_AFTER_ROUNDING=0 -DMSF_BUILD_ID='"tb"' $SRC tests/runner.c tests/sha256.c -o $C/runner_tb.exe 2>&1 | head -3
$C/runner_tb.exe verify tests/vectors/pack64.vec > $C/tininess.log 2>&1; why "7 wrong-tininess-polarity (pack64)" $? $C/tininess.log
