#!/usr/bin/env bash
# 41_vecxcheck.sh - cross-check MY decider vs all committed explog vectors.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
SRC="$COPY/src/msf16.c $COPY/src/msf32.c $COPY/src/msf64.c $COPY/src/msf_flags.c $COPY/src/msf_wide.c $COPY/src/msf_roundpack.c $COPY/src/msf_math.c"
gcc -std=c11 -O2 -Wall -Wextra -I"$D" -I"$COPY/include" -DMSF_EXPLOG_TEST_COUNTERS \
  "$D/vdriver.c" "$D/mydecider.c" $SRC -lmpfr -lgmp -o "$D/build/vdriver.exe" 2>&1 | tee "$D/build/build.log"
ulimit -v 4194304
START=$(date +%s)
for f in explog-f16 explog-f32 explog-f64; do
  "$D/build/vdriver.exe" vec "$COPY/tests/vectors/$f.vec" 2>&1 | tail -8 | tee -a "$D/41_vecxcheck.log"
done
echo "wall $(( $(date +%s) - START ))s" | tee -a "$D/41_vecxcheck.log"
