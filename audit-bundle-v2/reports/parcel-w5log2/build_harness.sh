#!/usr/bin/env bash
# build the explog differential harness (counters build)
set -eu
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w5-log2
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR="/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w5log2/tmp"
mkdir -p "$TMPDIR" build/explog
ulimit -v 4194304 2>/dev/null || true
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
gcc -std=c11 -O3 -Wall -Wextra -Werror -ffp-contract=off \
  -DMSF_EXPLOG_TEST_COUNTERS "$@" \
  $SRC tests/explog_exhaustive.c -lmpfr -lgmp \
  -o build/explog/explog_exhaustive.exe
echo BUILD-OK
