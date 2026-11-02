#!/usr/bin/env bash
# 29_tieprobe.sh - build modemap2 with and without TEST_COUNTERS; compare.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
SRC="$COPY/src/msf16.c $COPY/src/msf32.c $COPY/src/msf64.c $COPY/src/msf_flags.c $COPY/src/msf_wide.c $COPY/src/msf_roundpack.c $COPY/src/msf_math.c"
gcc -std=c11 -O2 -I"$COPY/include" "$D/modemap2.c" $SRC -o "$D/build/modemap2_plain.exe"
# shellcheck disable=SC2086
gcc -std=c11 -O2 -I"$COPY/include" -DMSF_EXPLOG_TEST_COUNTERS "$D/modemap2.c" $SRC -o "$D/build/modemap2_cnt.exe"
echo "== plain =="; "$D/build/modemap2_plain.exe"
echo "== counters =="; "$D/build/modemap2_cnt.exe"
echo "== vdriver one =="; "$D/build/vdriver.exe" one 2 0 c090cc0000000000
