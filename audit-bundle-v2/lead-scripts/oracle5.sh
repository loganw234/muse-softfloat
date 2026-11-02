#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/oracles || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=$PWD/tmp
export TMP="$(cygpath -w "$TMPDIR")" TEMP="$(cygpath -w "$TMPDIR")"
du -sh price-*.vec 2>/dev/null
rm -f price-*.vec
echo "price files deleted"
echo "--- header coverage retry ---"
H=SoftFloat-3e/source/include/softfloat.h
grep -c "f64_add" $H
grep -oE '(f16|f32|f64|ui32|ui64|i32|i64)_[A-Za-z0-9_]+' $H | sort -u > sf-functions.txt
wc -l sf-functions.txt
for pat in nextUp nextDown scaleB logB totalOrder isSignalingNaN mulAdd roundToInt rem; do
  echo "pattern $pat: $(grep -c "$pat" sf-functions.txt)"
done
grep -E '^(f16|f32|f64)_' sf-functions.txt | sed -E 's/^(f16|f32|f64)_//' | sort -u | tr '\n' ' '; echo
echo "--- softfloat flag/tininess enum values ---"
grep -nE 'softfloat_flag_|tininess_' SoftFloat-3e/source/include/softfloat_types.h SoftFloat-3e/source/include/softfloat.h | head -20
echo "--- testsoftfloat usage + per-function sampled ---"
TFB=TestFloat-3e/build/Linux-x86_64-GCC
$TFB/testsoftfloat -help > tsf-help.log 2>&1; head -20 tsf-help.log
for fn in f16_add f32_add f64_add f64_mul f64_div f64_sqrt f64_mulAdd f64_to_i32 f32_to_f64 f16_to_f32; do
  $TFB/testsoftfloat -level 1 $fn > "tsf-$fn.log" 2>&1
  echo "$fn rc=$? : $(tr '\r' '\n' < "tsf-$fn.log" | grep -E 'errors' | tail -1)"
done
echo "--- streaming pricing (wc only, no storage) ---"
for spec in "f64_div 2" "f64_mulAdd 2" "f32_sqrt 2" "f16_add 2" "f64_to_i64 2" "f32_to_f64 1" "f64_add 1" "f32_add 2"; do
  set -- $spec
  S=$(date +%s)
  N=$($TFB/testfloat_gen -level "$2" "$1" | wc -l)
  E=$(date +%s)
  echo "$1 level$2: lines=$N secs=$((E-S))"
done
