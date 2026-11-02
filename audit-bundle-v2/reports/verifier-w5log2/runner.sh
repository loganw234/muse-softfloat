#!/usr/bin/env bash
# runner.sh - build the committed runner outside the copy; verify the
# three committed explog vector files (no manifest gate: verdict only).
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
ulimit -v 4194304
cd "$SCR" || exit 9
SRC="$COPY/src/msf16.c $COPY/src/msf32.c $COPY/src/msf64.c $COPY/src/msf_flags.c $COPY/src/msf_wide.c $COPY/src/msf_roundpack.c $COPY/src/msf_string.c $COPY/src/msf_math.c $COPY/src/msf_alg.c"
# shellcheck disable=SC2086
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
  -I"$COPY/include" -I"$COPY/src" \
  $SRC "$COPY/tests/runner.c" "$COPY/tests/sha256.c" \
  -o build/msf_runner.exe > logs/runnerbuild.log 2>&1
echo "build rc=$?"
tail -3 logs/runnerbuild.log
./build/msf_runner.exe verify "$COPY/tests/vectors/explog-f16.vec" \
  "$COPY/tests/vectors/explog-f32.vec" \
  "$COPY/tests/vectors/explog-f64.vec" > logs/runnerexplog.log 2>&1
echo "verify rc=$?"
grep -E '^(file|prov|total|VERDICT|FAIL|MISMATCH)' logs/runnerexplog.log | head -30
