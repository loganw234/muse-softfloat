#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/oracles || exit 9
G=TestFloat-3e/build/Linux-x86_64-GCC/testfloat_gen
stripe() { echo "== $* =="; "$@" 2>&1 | head -3; }
stripe $G -help
stripe $G -level 1 f64_roundToInt
stripe $G -level 1 -rminMag f64_roundToInt
stripe $G -level 1 f64_to_i32
stripe $G -level 1 -rnear_maxMag f64_to_i32
stripe $G -level 1 f64_to_i32_r_minMag
stripe $G -level 1 f64_eq
stripe $G -level 1 f64_le_quiet
stripe $G -level 1 f64_isSignalingNaN
stripe $G -level 1 i32_to_f64
stripe $G -level 1 ui64_to_f32
stripe $G -level 1 f64_rem
echo "== inexact presence in roundToInt near_even (flags byte counts) =="
$G -level 1 f64_roundToInt | awk '{print $NF}' | sort | uniq -c | head
echo "== to_i32 near_even flags distribution =="
$G -level 1 f64_to_i32 | awk '{print $NF}' | sort | uniq -c | head
