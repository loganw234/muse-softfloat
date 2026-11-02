#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/oracles || exit 9
TFB=TestFloat-3e/build/Linux-x86_64-GCC
for spec in "f32_sqrt 1" "f16_add 1" "f64_to_i64 1" "f32_to_f64 1" "f32_add 1" "f64_mulAdd 1" "f16_mulAdd 1" "f64_rem 1" "f64_roundToInt 1"; do
  set -- $spec
  S=$(date +%s)
  N=$($TFB/testfloat_gen -level "$2" "$1" | wc -l)
  E=$(date +%s)
  echo "$1 level$2: lines=$N secs=$((E-S))"
done
echo "--- sample case lines per shape ---"
$TFB/testfloat_gen -level 1 f64_add | head -2
$TFB/testfloat_gen -level 1 f64_to_i32 | head -2
$TFB/testfloat_gen -level 1 -rmin f64_add | head -1
$TFB/testfloat_gen -level 1 -rnear_maxMag f64_add | head -1
