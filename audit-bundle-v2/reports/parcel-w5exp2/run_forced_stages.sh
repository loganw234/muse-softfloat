#!/usr/bin/env bash
# Force-start corroboration: the same wc + f16 differentials
# with the kernel forced to start at stage 2, then stage 3.
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w5-exp2
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
BASE=../../scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94/src/binary64
for st in 1 2; do
    gcc -std=c11 -O3 -Wall -Wextra -Werror -ffp-contract=off \
        -DMSF_EXPLOG_TEST_COUNTERS -DMSF_EXPLOG_FORCE_START=$st \
        $SRC tests/explog_exhaustive.c -lmpfr -lgmp \
        -o build/explog/harness-force$st.exe || exit 1
    echo "=== FORCE_START=$st ==="
    ./build/explog/harness-force$st.exe f16 | tail -2
    ./build/explog/harness-force$st.exe wc exp2 "$BASE/exp2/exp2.wc" | tail -3
    ./build/explog/harness-force$st.exe wc exp2m1 "$BASE/exp2m1/exp2m1.wc" | tail -3
    ./build/explog/harness-force$st.exe f64seed 424242 50000 | tail -2
done
