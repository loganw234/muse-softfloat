#!/usr/bin/env bash
# 34_rebuild_retest.sh - rebuild driver with new decider, rerun selftest.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
SRC="$COPY/src/msf16.c $COPY/src/msf32.c $COPY/src/msf64.c $COPY/src/msf_flags.c $COPY/src/msf_wide.c $COPY/src/msf_roundpack.c $COPY/src/msf_math.c"
gcc -std=c11 -O2 -Wall -Wextra -I"$D" -I"$COPY/include" -DMSF_EXPLOG_TEST_COUNTERS \
  "$D/vdriver.c" "$D/mydecider.c" $SRC -lmpfr -lgmp -o "$D/build/vdriver.exe" 2>&1 | tee "$D/build/build.log"
python3 "$D/25_selftest.py" 2>&1 | tee "$D/34_selftest.log"
