#!/usr/bin/env bash
# ownharness.sh - build the COPY's own exhaustive harness outside the
# copy, run the same cells through the parcel's decider.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
ulimit -v 4194304
cd "$SCR" || exit 9
SRC="$COPY/src/msf16.c $COPY/src/msf32.c $COPY/src/msf64.c $COPY/src/msf_flags.c $COPY/src/msf_wide.c $COPY/src/msf_roundpack.c $COPY/src/msf_string.c $COPY/src/msf_math.c $COPY/src/msf_alg.c"
# shellcheck disable=SC2086
gcc -std=c11 -O2 -Wall -Wextra -ffp-contract=off \
  -DMSF_EXPLOG_TEST_COUNTERS -DMSF_TRIG_TEST_COUNTERS \
  -I"$COPY/include" -I"$COPY/src" \
  "$COPY/tests/explog_exhaustive.c" $SRC -o build/own_exhaustive.exe -lmpfr -lgmp \
  > logs/ownharness.log 2>&1
echo "build rc=$?"
tail -3 logs/ownharness.log
for cell in "f64 log2 3ff0000000000000" "f64 log2 4000000000000000" \
  "f16 log2 0001" "f64 log2p1 3ff0000000000000"; do
  # shellcheck disable=SC2086
  echo "--- $cell"
  echo "" | ./build/own_exhaustive.exe one $cell 2>&1 | tail -8
done
