#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/oracles || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=$PWD/tmp
export TMP="$(cygpath -w "$TMPDIR")" TEMP="$(cygpath -w "$TMPDIR")"
TFB=TestFloat-3e/build/Linux-x86_64-GCC
echo "--- testsoftfloat full sampled log (CR-safe) ---"
tr '\r' '\n' < testsoftfloat.log | grep -E 'Testing|errors' | head -30
echo "--- header coverage: f16/f32/f64 functions in softfloat.h ---"
grep -oE '\b(f16|f32|f64|ui32|ui64|i32|i64)_[A-Za-z0-9_]+' SoftFloat-3e/source/include/softfloat.h | sort -u > sf-functions.txt
wc -l sf-functions.txt
for pat in nextUp nextDown scaleB logB totalOrder class isSignaling isNaN decimal min max; do
  echo "pattern $pat: $(grep -ci "$pat" sf-functions.txt)"
done
grep -E 'mulAdd|rem\b|roundToInt|isSignaling' sf-functions.txt | head -20
echo "--- probes ---"
gcc -std=c11 -O2 -ffp-contract=off -I SoftFloat-3e/source/include probe_intconv.c SoftFloat-3e/build/Linux-x86_64-GCC/softfloat.a -o probe_intconv.exe && ./probe_intconv.exe
echo "intconv rc=$?"
cd ../../muse-softfloat || exit 9
gcc -std=c11 -O2 -ffp-contract=off -I ../scratch/oracles/SoftFloat-3e/source/include -I include \
  ../scratch/oracles/probe_snan_xcheck.c src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c \
  ../scratch/oracles/SoftFloat-3e/build/Linux-x86_64-GCC/softfloat.a -o ../scratch/oracles/probe_snan.exe \
  && ../scratch/oracles/probe_snan.exe
echo "snan xcheck rc=$?"
echo "--- vector pricing (counts + seconds, to files) ---"
cd ../scratch/oracles || exit 9
for spec in "f64_add 1" "f64_add 2" "f64_div 2" "f64_mulAdd 2" "f32_sqrt 2" "f16_add 2" "f64_to_i64 2" "f32_to_f64 1"; do
  set -- $spec
  S=$(date +%s)
  $TFB/testfloat_gen -level "$2" "$1" > "price-$1-l$2.vec" 2> "price-$1-l$2.err"
  rc=$?
  E=$(date +%s)
  echo "$1 level$2: rc=$rc lines=$(wc -l < "price-$1-l$2.vec") bytes=$(wc -c < "price-$1-l$2.vec") secs=$((E-S))"
  head -2 "price-$1-l$2.vec"
done
