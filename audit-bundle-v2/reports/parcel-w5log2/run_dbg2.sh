#!/usr/bin/env bash
set -eu
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT/worktrees/w5-log2"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_alg.c"
gcc -std=c11 -O1 -Wall -Wextra -ffp-contract=off \
  $SRC ../../scratch/parcel-w5log2/dbg2.c -o build/explog/dbg2.exe
./build/explog/dbg2.exe
