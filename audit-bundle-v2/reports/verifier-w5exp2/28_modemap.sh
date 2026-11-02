#!/usr/bin/env bash
# 28_modemap.sh - verify verifier mode passing via an established add tie.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
gcc -std=c11 -O2 -I"$COPY/include" "$D/modemap.c" "$COPY/src/msf16.c" \
  "$COPY/src/msf32.c" "$COPY/src/msf64.c" "$COPY/src/msf_flags.c" \
  "$COPY/src/msf_wide.c" "$COPY/src/msf_roundpack.c" "$COPY/src/msf_math.c" \
  -o "$D/build/modemap.exe" 2>&1 | tee "$D/build/modemap.log"
"$D/build/modemap.exe" 2>&1 | tee "$D/28_modemap.log"
