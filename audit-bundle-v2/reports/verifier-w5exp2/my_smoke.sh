#!/usr/bin/env bash
# verifier second-attempt: build copy runner into scratch (copy untouched).
set -u
cd /mnt/c/Users/logan/source/repos/Muse-Softfloat
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
  -DMSF_BUILD_ID='"verifier-w5exp2"' \
  -I worktrees/verify5-exp2/include \
  worktrees/verify5-exp2/src/msf16.c \
  worktrees/verify5-exp2/src/msf32.c \
  worktrees/verify5-exp2/src/msf64.c \
  worktrees/verify5-exp2/src/msf_flags.c \
  worktrees/verify5-exp2/src/msf_wide.c \
  worktrees/verify5-exp2/src/msf_roundpack.c \
  worktrees/verify5-exp2/src/msf_string.c \
  worktrees/verify5-exp2/src/msf_math.c \
  worktrees/verify5-exp2/src/msf_alg.c \
  worktrees/verify5-exp2/tests/runner.c \
  worktrees/verify5-exp2/tests/sha256.c \
  -o scratch/verifier-w5exp2/smoke/msf_runner.exe \
  > scratch/verifier-w5exp2/smoke/build.log 2>&1 || { tail -20 scratch/verifier-w5exp2/smoke/build.log; exit 1; }
echo RUNNER-OK
./scratch/verifier-w5exp2/smoke/msf_runner.exe unit > scratch/verifier-w5exp2/smoke/unit.log 2>&1 || { tail -10 scratch/verifier-w5exp2/smoke/unit.log; exit 1; }
grep -E 'unit (sha256|flags|versions|wide)|unit:' scratch/verifier-w5exp2/smoke/unit.log
