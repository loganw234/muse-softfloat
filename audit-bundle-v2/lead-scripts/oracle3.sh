#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/oracles || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=$PWD/tmp
mkdir -p "$TMPDIR"
export TMP="$(cygpath -w "$TMPDIR")" TEMP="$(cygpath -w "$TMPDIR")"
MAKE="env TMPDIR=$TMPDIR TMP=$TMP TEMP=$TEMP make"
echo "--- SoftFloat build ---"
cd SoftFloat-3e/build/Linux-x86_64-GCC || exit 9
$MAKE > ../../../sf-build.log 2>&1; echo "sf rc=$?"; tail -2 ../../../sf-build.log
ls -la softfloat.a 2>/dev/null || ls
grep -c "Error" ../../../sf-build.log || true
cd ../../../TestFloat-3e/build/Linux-x86_64-GCC || exit 9
echo "--- TestFloat build ---"
$MAKE > ../../../tf-build.log 2>&1; echo "tf rc=$?"; tail -3 ../../../tf-build.log
ls *.exe 2>/dev/null
echo "--- testsoftfloat sampled self-check ---"
./testsoftfloat f16_add f32_add f64_add f64_mul f64_div f64_sqrt f64_mulAdd f64_to_i32 f32_to_f64 f16_to_f32 > ../../../testsoftfloat.log 2>&1
echo "testsoftfloat rc=$?"
cat ../../../testsoftfloat.log
