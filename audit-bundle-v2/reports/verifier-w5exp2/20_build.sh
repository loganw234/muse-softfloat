#!/usr/bin/env bash
# 20_build.sh - build verifier driver against the UNMODIFIED copy.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
OUT="$D/build"
mkdir -p "$OUT"
# copy status guard: refuse if copy is dirty
if [ -n "$(git -C "$COPY" status --short)" ]; then
  echo "REFUSED: copy worktree is dirty; not building"
  exit 1
fi
echo "copy HEAD: $(git -C "$COPY" rev-parse HEAD)"
SRC="$COPY/src/msf16.c $COPY/src/msf32.c $COPY/src/msf64.c $COPY/src/msf_flags.c $COPY/src/msf_wide.c $COPY/src/msf_roundpack.c $COPY/src/msf_math.c"
gcc -std=c11 -O2 -Wall -Wextra -I"$COPY/include" -DMSF_EXPLOG_TEST_COUNTERS \
  "$D/vdriver.c" "$D/mydecider.c" $SRC -lmpfr -lgmp -o "$OUT/vdriver.exe" 2>&1 | tee "$OUT/build.log"
[ -x "$OUT/vdriver.exe" ] && echo "BUILD OK" || { echo "BUILD FAIL"; exit 1; }
