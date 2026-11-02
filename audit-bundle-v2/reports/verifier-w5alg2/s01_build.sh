#!/usr/bin/env bash
# s01_build.sh - build verifier probe binaries from the COPY's sources.
# The copy (worktrees/verify5-alg2) is never modified; all outputs go
# to scratch/verifier-w5alg2/out/.
set -e -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-$(pwd)/.venv/Scripts/python.exe}"
export TMPDIR="$(pwd)/scratch/verifier-w5alg2/tmp"
export TMP="$TMPDIR" TEMP="$TMPDIR"
mkdir -p "$TMPDIR" scratch/verifier-w5alg2/out
ulimit -v 4194304
COPY=worktrees/verify5-alg2
OUT=scratch/verifier-w5alg2/out
SRC="$COPY/src/msf16.c $COPY/src/msf32.c $COPY/src/msf64.c $COPY/src/msf_flags.c $COPY/src/msf_wide.c $COPY/src/msf_roundpack.c $COPY/src/msf_string.c $COPY/src/msf_math.c $COPY/src/msf_alg.c"
CFLAGS="-std=c11 -O2 -Wall -Wextra -ffp-contract=off"
gcc $CFLAGS -I$COPY/include -I$COPY/src $SRC scratch/verifier-w5alg2/harness.c -o $OUT/harness_floor.exe 2>&1 | tee $OUT/harness_floor.warnings
echo "built harness_floor.exe"
gcc $CFLAGS -DMSF_ALG_TEST_JAM -I$COPY/include -I$COPY/src $SRC scratch/verifier-w5alg2/harness.c -o $OUT/harness_jam.exe 2>&1 | tee $OUT/harness_jam.warnings
echo "built harness_jam.exe"
# NOSTICKY intentionally not built: in this copy the
# MSF_ALG_TEST_NOSTICKY arm recompiles to the same remainder-only
# sticky as the floor build (a no-op macro), recorded as a finding.
gcc $CFLAGS -I$COPY/include -I$COPY/src -I/c/msys64/mingw64/include $COPY/tests/alg_decider.c $SRC -L/c/msys64/mingw64/lib -lmpfr -lgmp -o $OUT/alg_decider.exe
echo "built alg_decider.exe (MPFR oracle decider, test-only)"
ls -la $OUT/
