#!/usr/bin/env bash
# 40_runner3.sh - build copy runner, verify the 3 E_tie ta lines.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
OUT="$D/build"
SRC="$COPY/src/msf16.c $COPY/src/msf32.c $COPY/src/msf64.c $COPY/src/msf_flags.c $COPY/src/msf_wide.c $COPY/src/msf_roundpack.c $COPY/src/msf_string.c $COPY/src/msf_math.c $COPY/src/msf_alg.c"
# shellcheck disable=SC2086
gcc -std=c11 -O2 -Wall -Wextra -I"$COPY/include" -DMSF_BUILD_ID="\"verifier\"" \
  $SRC "$COPY/tests/runner.c" "$COPY/tests/sha256.c" \
  -o "$OUT/msf_runner.exe" 2>&1 | tee "$OUT/runner-build.log"
printf '%s\n' \
  "msf64_exp2 ta c090cc0000000000 -> 1 18 mpfr-explog:integers" \
  "msf32_exp2 ta c3160000 -> 1 18 mpfr-explog:integers" \
  "msf16_exp2 ta ce40 -> 1 18 mpfr-explog:integers" \
  > "$OUT/tie3.vec"
"$OUT/msf_runner.exe" verify "$OUT/tie3.vec" 2>&1 | tee "$D/40_runner3.log"
