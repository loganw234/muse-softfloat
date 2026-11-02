#!/usr/bin/env bash
# ownharness2.sh - correct numeric one-mode invocation.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
ulimit -v 4194304
cd "$SCR" || exit 9
# fi: 0=f16 1=f32 2=f64 ; fn: 2=log2 3=log2p1
for cell in "2 2 3ff0000000000000" "2 2 4000000000000000" \
  "0 2 0001" "2 3 3ff0000000000000" "2 3 bfe0000000000000" \
  "1 2 3f800000" "0 2 3c00"; do
  # shellcheck disable=SC2086
  echo "--- one $cell"
  ./build/own_exhaustive.exe one $cell 2>&1 | tail -6
done
