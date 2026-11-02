#!/usr/bin/env bash
# Forced-stage corroboration: FORCE_START=1 and =2 reruns of
# wc log pair + f16 + seeded must be identical PASS.
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT/worktrees/w5-log2"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR="$ROOT/scratch/parcel-w5log2/tmp"
mkdir -p "$TMPDIR" build/explog/forced
ulimit -v 4194304 2>/dev/null || true
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
PIN=../../scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94/src/binary64
fail=0
for st in 1 2; do
    gcc -std=c11 -O3 -Wall -Wextra -Werror -ffp-contract=off \
        -DMSF_EXPLOG_TEST_COUNTERS -DMSF_EXPLOG_FORCE_START=$st \
        $SRC tests/explog_exhaustive.c -lmpfr -lgmp \
        -o "build/explog/forced/h$st.exe" || { echo "build $st failed"; exit 1; }
    echo "=== FORCE_START=$st wc log2 ==="
    "build/explog/forced/h$st.exe" wc log2 "$PIN/log2/log2.wc" 2>&1 | grep -E "counters|PASS|FAIL" || fail=1
    echo "=== FORCE_START=$st wc log2p1 ==="
    "build/explog/forced/h$st.exe" wc log2p1 "$PIN/log2p1/log2p1.wc" 2>&1 | grep -E "counters|PASS|FAIL" || fail=1
    echo "=== FORCE_START=$st f16 ==="
    "build/explog/forced/h$st.exe" f16 2>&1 | grep -E "counters|PASS|FAIL" || fail=1
    echo "=== FORCE_START=$st f64seed ==="
    "build/explog/forced/h$st.exe" f64seed 20261028 200000 2>&1 | grep -E "counters|PASS|FAIL" || fail=1
done
[ "$fail" -eq 0 ] && echo "FORCED: DONE" || echo "FORCED: FAIL"
exit "$fail"
