#!/usr/bin/env bash
# mutants.sh - verifier-w5aug: build probe binaries with each
# MSF_AUG_TEST_* mutant switch and diff their one-cell behaviour
# against the shipped baseline. Read-only w.r.t. the copy.
set -u
cd "$(dirname "$0")" || exit 9
COPY=../../worktrees/verify5-aug
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
CC="${MSF_CC:-gcc}"
ulimit -v 3000000 2>/dev/null || true
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
fail() { echo "MUTANTS.SH: FAIL - $1"; exit 1; }
for m in TE_HEAD ZERO_TAIL_SIGN SWAP_PAIR JAM_WINDOW P1_OPPOSITE PACK_LEAK; do
  "$CC" -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -I"$COPY/include" \
    -DMSF_AUG_TEST_$m $(for f in $SRC; do echo "$COPY/$f"; done) ./probe_aug.c \
    -o "build/probe_$m.exe" > "build/build-$m.log" 2>&1 \
    || { cat "build/build-$m.log"; fail "mutant $m build"; }
  echo "built probe_$m.exe"
done
echo MUTANTS.SH: OK
