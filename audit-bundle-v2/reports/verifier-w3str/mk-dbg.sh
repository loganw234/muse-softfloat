#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$R/scratch/verifier-w3str/tmp
export TMP="C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w3str\tmp"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/worktrees/verify3-str" || exit 9
gcc -std=c11 -O2 -Wall -Wextra -Wno-unused-parameter -ffp-contract=off \
  -Iinclude -Isrc "$R/scratch/verifier-w3str/vw_dbg.c" \
  src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c \
  src/msf_roundpack.c src/msf_string.c \
  -o "$R/scratch/verifier-w3str/vw_dbg.exe" 2>&1
"$R/scratch/verifier-w3str/vw_dbg.exe"
