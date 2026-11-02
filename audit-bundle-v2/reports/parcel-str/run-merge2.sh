#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=$ROOT/scratch/parcel-str/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR"
cd "$W" || exit 9
git -c safe.directory="$W" merge --no-edit main
echo "merge rc=$?"
git -c safe.directory="$W" log --oneline -3
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -c src/msf_string.c -o "$ROOT/scratch/parcel-str/msf_string.o"
echo "host compile rc=$?"
wc -l src/msf_string.c
