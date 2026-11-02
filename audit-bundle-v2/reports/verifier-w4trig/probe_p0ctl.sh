#!/bin/bash
# Probe T: P0 control subset replicated from scratch against the
# runner vehicle (validates the vehicle used for vector replay).
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
C=$ROOT/worktrees/verify4-trig
R=$V/tmp/msf_runner.exe
cd "$ROOT" || exit 9
mkdir -p $V/tmp/ctrl
cd $C || exit 9
echo "--- c1 corrupted expected bit (must refuse) ---"
awk 'BEGIN{d=0} /^msf16_is_signaling/ && !d {for(i=1;i<=NF;i++) if($i=="->") $(i+1)=($(i+1)=="1"?"0":"1"); d=1} {print}' \
  tests/vectors/encodings-f16.vec > $V/tmp/ctrl/corrupt.vec
$R verify $V/tmp/ctrl/corrupt.vec > $V/tmp/ctrl/c1.log 2>&1
echo "rc=$? (expect nonzero)"; grep -c 'VERDICT: FAIL' $V/tmp/ctrl/c1.log
echo "--- c3 wrong rounding mode pack64 te<->tz (must refuse) ---"
awk '{if($1=="internal.pack64"){if($2=="te")$2="tz"; else if($2=="tz")$2="te"} print}' \
  tests/vectors/pack64.vec > $V/tmp/ctrl/wrongrm.vec
$R verify $V/tmp/ctrl/wrongrm.vec > $V/tmp/ctrl/c3.log 2>&1
echo "rc=$? (expect nonzero)"
echo "--- c7 wrong-tininess-polarity build (must refuse pack64) ---"
gcc -std=c11 -O2 -Wall -Wextra -ffp-contract=off -Wno-error \
  -DMSF_TININESS_AFTER_ROUNDING=0 \
  $C/src/msf16.c $C/src/msf32.c $C/src/msf64.c $C/src/msf_flags.c \
  $C/src/msf_wide.c $C/src/msf_roundpack.c $C/src/msf_string.c \
  $C/src/msf_math.c $C/tests/runner.c $C/tests/sha256.c \
  -o $V/tmp/ctrl/runner_before.exe 2>/dev/null
echo "tininess build rc=$?"
$V/tmp/ctrl/runner_before.exe verify tests/vectors/pack64.vec > $V/tmp/ctrl/c7.log 2>&1
echo "rc=$? (expect nonzero)"; grep -c '^FAIL' $V/tmp/ctrl/c7.log
