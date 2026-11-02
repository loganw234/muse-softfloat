#!/usr/bin/env bash
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-demo" || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=$PWD/demo/cache/tmp
mkdir -p "$TMPDIR" demo/cache/build
export TMP=$(cygpath -w "$TMPDIR"); export TEMP=$TMP
PY=python
CC=gcc
B=demo/cache/build
EX=demo/cache/ias15-extract
KF=demo/cache/kissfft-tree
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
echo "cc: $($CC -dumpmachine) $($CC -dumpversion)"
date

echo "== IAS15 native =="
NF="-std=c99 -O3 -march=x86-64 -ffp-contract=off -fno-fast-math -fno-unsafe-math-optimizations -fexcess-precision=standard -Wall -Wextra -Wno-unused-parameter"
$CC $NF -I$EX -Iboard -I. $EX/integrator_ias15_min.c $EX/gravity_basic_min.c $EX/sim_min.c $EX/ias15x.c board/ias15_hash.c tests/sha256.c demo/ias15_host_main.c -o $B/ias15_native.exe -lm > $B/ias15-native-build.log 2>&1
echo "build exit=$?"; cat $B/ias15-native-build.log
time $B/ias15_native.exe 2000 $B/hashes_native.txt; echo "run exit=$?"
$PY demo/compare_ias15.py demo/expected-ias15.txt $B/hashes_native.txt; echo "compare exit=$?"

echo "== IAS15 soft =="
SF="-std=c99 -O3 -msoft-float -mno-sse2 -ffp-contract=off -fno-fast-math -fno-unsafe-math-optimizations -fno-builtin-fabs -fno-builtin-copysign -fno-builtin-sqrt -Wall -Wno-unused-parameter"
$CC $SF -DDEMO_IAS15_SOFT -I$EX -Iboard -I. -Iinclude -Isrc $EX/integrator_ias15_min.c $EX/gravity_basic_min.c $EX/sim_min.c $EX/ias15x.c board/ias15_hash.c tests/sha256.c demo/ias15_host_main.c demo/ias15_host_shim.c $SRC -o $B/ias15_soft.exe -lm > $B/ias15-soft-build.log 2>&1
echo "build exit=$?"; cat $B/ias15-soft-build.log
time $B/ias15_soft.exe 2000 $B/hashes_soft.txt; echo "run exit=$?"
grep SHIMOPS $B/hashes_soft.txt
$PY demo/compare_ias15.py demo/expected-ias15.txt $B/hashes_soft.txt; echo "compare exit=$?"

echo "== KissFFT =="
KFF="-std=c11 -O2 -Wall -Wextra -ffp-contract=off -fno-fast-math -fno-builtin-sinpi -fno-builtin-cospi -fno-builtin-floor -fno-builtin-sqrt -Dkiss_fft_scalar=double"
$CC $KFF -I. -Icompat -I$KF demo/kissfft_host_main.c $KF/kiss_fft.c $KF/kiss_fftr.c $SRC compat/msf_aeabi.c demo/kissfft_host_shim.c tests/sha256.c -Wl,--wrap=sinpi,--wrap=cospi,--wrap=floor -lm -o $B/kissfft_host.exe > $B/kissfft-build.log 2>&1
echo "build exit=$?"; cat $B/kissfft-build.log
$B/kissfft_host.exe > $B/kissfft-out.txt 2>&1; echo "run exit=$?"
cat $B/kissfft-out.txt
grep '^KF ' demo/expected-kissfft.txt > $B/kf-expect.txt
grep '^KF ' $B/kissfft-out.txt > $B/kf-got.txt
diff $B/kf-expect.txt $B/kf-got.txt && echo "KF ROWS IDENTICAL"

echo "== interval =="
IFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"
$CC $IFLAGS $SRC tests/sha256.c board/interval_workload.c board/interval_host.c -o $B/interval_host.exe > $B/interval-build.log 2>&1
echo "build exit=$?"; cat $B/interval-build.log
time $B/interval_host.exe tests/interval_catalogue.tsv > $B/interval-out.txt 2>&1; echo "run exit=$?"
grep -E '^SUMMARY|^HOST_SHA256' $B/interval-out.txt
cat demo/expected-interval.txt
echo "HOST-PROOFS-TEST DONE"
date
