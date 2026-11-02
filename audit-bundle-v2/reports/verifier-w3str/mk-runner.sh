#!/usr/bin/env bash
# probe build for verifier-w3str (read-only against the copy).
R=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$R/scratch/verifier-w3str/tmp
export TMP="C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w3str\tmp"
export TEMP="$TMP"
mkdir -p "$TMPDIR"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/worktrees/verify3-str" || exit 9
gcc -std=c11 -O2 -Wall -Wextra -Wno-unused-parameter -ffp-contract=off \
  src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c \
  src/msf_roundpack.c src/msf_string.c tests/runner.c tests/sha256.c \
  -o "$R/scratch/verifier-w3str/runner.exe" \
  > "$R/scratch/verifier-w3str/build.log" 2>&1
echo "exit=$?"
tail -5 "$R/scratch/verifier-w3str/build.log"
