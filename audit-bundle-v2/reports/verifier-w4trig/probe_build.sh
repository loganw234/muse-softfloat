#!/bin/bash
# Probe C: copy cleanliness, exact run.sh host-build (Werror) verdict,
# ARM toolchain presence, .wc oracle files, trig harness usage.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
echo "--- git status (copy) ---"
git -C worktrees/verify4-trig status --short | head -20
git -C worktrees/verify4-trig log --oneline -3
git -C worktrees/verify4-trig diff HEAD --stat | tail -5
echo "--- exact run.sh host build of copy sources ---"
cd worktrees/verify4-trig
mkdir -p ../scratch/verifier-w4trig/tmp
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
  src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c \
  src/msf_roundpack.c src/msf_string.c src/msf_math.c \
  tests/runner.c tests/sha256.c -o ../scratch/verifier-w4trig/tmp/runner-werror.exe \
  > ../scratch/verifier-w4trig/log_werror_build.txt 2>&1
echo "werror build rc=$?"
head -10 ../scratch/verifier-w4trig/log_werror_build.txt
echo "--- ARM toolchain ---"
command -v arm-none-eabi-gcc
echo "--- oracle .wc files ---"
ls -la ../../scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94/binary64/ 2>/dev/null | head
find ../../scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94 -name '*.wc' 2>/dev/null | head
