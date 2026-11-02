#!/usr/bin/env bash
# build.sh - verifier-w5aug host build of the verify5-aug COPY (read-only).
# Never writes into the copy: all outputs land in scratch/verifier-w5aug/build.
set -u
cd "$(dirname "$0")" || exit 9
COPY=../../worktrees/verify5-aug
BLD=$PWD/build
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe}"
# x86-64 gcc needs its bindir on PATH (DLL resolution); with the
# export above it builds cleanly, matching tools/run.sh. (A bare
# absolute-path invocation without that PATH fails in cc1.)
CC="${MSF_CC:-gcc}"
ulimit -v 3000000 2>/dev/null || true
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
fail() { echo "BUILD.SH: FAIL - $1"; exit 1; }
echo "cc: $($CC -dumpmachine) $($CC -dumpversion)"
echo "python: $MSF_PYTHON ($("$MSF_PYTHON" --version 2>&1))"
# 1. probe driver (single-case kernel calls)
"$CC" -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -I"$COPY/include" \
  $(for f in $SRC; do echo "$COPY/$f"; done) ./probe_aug.c -o "$BLD/probe_aug.exe" \
  > "$BLD/build-probe.log" 2>&1 || { cat "$BLD/build-probe.log"; fail "probe build"; }
echo "built probe_aug.exe"
# 2. committed two-result runner
"$CC" -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -I"$COPY/include" -I"$COPY/tests" \
  $(for f in $SRC; do echo "$COPY/$f"; done) "$COPY/tests/runner.c" "$COPY/tests/sha256.c" \
  -o "$BLD/runner.exe" > "$BLD/build-runner.log" 2>&1 || { cat "$BLD/build-runner.log"; fail "runner build"; }
echo "built runner.exe"
# 3. f16 differential harness, COMMITTED unmodified (needs __int128,
# hence the x86-64 compiler above) plus the verifier-adapted copy
# (u128 -> uint64_t; faithfulness cross-checked against myref.py
# before any verdict from it is quoted)
"$CC" -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -I"$COPY/include" \
  $(for f in $SRC; do echo "$COPY/$f"; done) "$COPY/tests/aug_exhaustive.c" \
  -o "$BLD/aug_exhaustive_committed.exe" > "$BLD/build-aug.log" 2>&1 || { cat "$BLD/build-aug.log"; fail "committed aug harness build"; }
echo "built committed aug_exhaustive.exe"
"$CC" -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -I"$COPY/include" \
  $(for f in $SRC; do echo "$COPY/$f"; done) ./aug_exhaustive_adapted.c \
  -o "$BLD/aug_exhaustive_adapted.exe" >> "$BLD/build-aug.log" 2>&1 || { cat "$BLD/build-aug.log"; fail "adapted aug harness build"; }
echo "built aug_exhaustive_adapted.exe"
echo BUILD.SH: OK
