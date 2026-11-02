#!/usr/bin/env bash
# 27_copyharness.sh - build the COPY's own exhaustive harness (unmodified
# sources) in verifier scratch, to cross-check mode passing on tie cells.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
OUT="$D/build"
gcc -std=c11 -O2 -Wall -Wextra -I"$COPY/include" -I"$COPY/src" -DMSF_EXPLOG_TEST_COUNTERS \
  "$COPY/tests/explog_exhaustive.c" \
  "$COPY/src/msf16.c" "$COPY/src/msf32.c" "$COPY/src/msf64.c" \
  "$COPY/src/msf_flags.c" "$COPY/src/msf_wide.c" "$COPY/src/msf_roundpack.c" \
  "$COPY/src/msf_math.c" -lmpfr -lgmp -o "$OUT/copy_exhaustive.exe" 2>&1 | tee "$OUT/copyharness.log"
[ -x "$OUT/copy_exhaustive.exe" ] && echo "COPY HARNESS BUILD OK" || { echo "COPY HARNESS BUILD FAIL"; exit 1; }
"$OUT/copy_exhaustive.exe" one 2 0 c090cc0000000000
echo "--- mine ---"
"$OUT/vdriver.exe" one 2 0 c090cc0000000000
