#!/usr/bin/env bash
# build.sh - build verifier-owned vlog2 (own decider+driver) outside
# the copy. Kernel sources are compiled read-only from the copy;
# all outputs land in scratch/verifier-w5log2/build.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
GCC=gcc
ulimit -v 4194304
mkdir -p "$SCR/build"
cd "$SCR" || exit 9
SRC="$COPY/src/msf16.c $COPY/src/msf32.c $COPY/src/msf64.c $COPY/src/msf_flags.c $COPY/src/msf_wide.c $COPY/src/msf_roundpack.c $COPY/src/msf_string.c $COPY/src/msf_math.c $COPY/src/msf_alg.c"
# shellcheck disable=SC2086
"$GCC" -std=c11 -O2 -Wall -Wextra -ffp-contract=off \
  -DMSF_EXPLOG_TEST_COUNTERS -DMSF_TRIG_TEST_COUNTERS \
  -I"$COPY/include" -I"$COPY/src" \
  vlog2.c $SRC -o build/vlog2.exe \
  -I/c/msys64/mingw64/include -L/c/msys64/mingw64/lib -lmpfr -lgmp \
  > logs/build.log 2>&1
echo "build exit=$?"
tail -5 logs/build.log
ls -la build/vlog2.exe
