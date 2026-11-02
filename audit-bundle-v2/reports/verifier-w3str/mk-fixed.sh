#!/usr/bin/env bash
# Fault-isolation diagnostic ONLY: scratch copy of the TU with three
# one-line fixes; never touches worktrees/verify3-str.
R=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$R/scratch/verifier-w3str/tmp
export TMP="C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w3str\tmp"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p "$R/scratch/verifier-w3str/fixed"
cd "$R/scratch/verifier-w3str" || exit 9
cp "$R/worktrees/verify3-str/src/msf_string.c" fixed/msf_string_fixed.c
"$R/.venv/Scripts/python.exe" patch-fixed.py
cd "$R/worktrees/verify3-str" || exit 9
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
  -Iinclude -Isrc \
  src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c \
  src/msf_roundpack.c \
  "$R/scratch/verifier-w3str/fixed/msf_string_fixed.c" \
  tests/runner.c tests/sha256.c \
  -o "$R/scratch/verifier-w3str/fixed/runner-fixed.exe" \
  > "$R/scratch/verifier-w3str/fixed/build.log" 2>&1
echo "strict build exit=$? (Werror re-enabled: proves -Wunused-parameter clean)"
tail -3 "$R/scratch/verifier-w3str/fixed/build.log"
"$R/scratch/verifier-w3str/fixed/runner-fixed.exe" verify \
  tests/vectors/from-decimal-str.vec tests/vectors/from-hex-str.vec \
  tests/vectors/to-decimal-str.vec tests/vectors/to-hex-str.vec \
  > "$R/scratch/verifier-w3str/fixed/replay.log" 2>&1
echo "replay exit=$?"
grep -E '^(file|total|VERDICT)' "$R/scratch/verifier-w3str/fixed/replay.log"
grep '^FAIL' "$R/scratch/verifier-w3str/fixed/replay.log" | head -20
