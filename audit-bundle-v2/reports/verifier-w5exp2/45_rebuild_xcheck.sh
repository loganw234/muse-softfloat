#!/usr/bin/env bash
# 45_rebuild_xcheck.sh - rebuild, selftest, then full vec cross-check.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
SRC="$COPY/src/msf16.c $COPY/src/msf32.c $COPY/src/msf64.c $COPY/src/msf_flags.c $COPY/src/msf_wide.c $COPY/src/msf_roundpack.c $COPY/src/msf_math.c"
gcc -std=c11 -O2 -Wall -Wextra -I"$D" -I"$COPY/include" -DMSF_EXPLOG_TEST_COUNTERS \
  "$D/vdriver.c" "$D/mydecider.c" $SRC -lmpfr -lgmp -o "$D/build/vdriver.exe" 2>&1 | tee "$D/build/build.log"
[ -x "$D/build/vdriver.exe" ] || { echo "BUILD FAIL"; exit 1; }
python3 "$D/25_selftest.py" 2>&1 | tail -6 | tee "$D/45_selftest.log"
ulimit -v 4194304
START=$(date +%s)
for f in explog-f16 explog-f32 explog-f64; do
  "$D/build/vdriver.exe" vec "$COPY/tests/vectors/$f.vec" > "$D/45_$f.log" 2>&1
  tail -1 "$D/45_$f.log"
done
echo "wall $(( $(date +%s) - START ))s"
