#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
S=$ROOT/scratch/parcel-str
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=$S/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
cd "$W" || exit 9
git -c safe.directory="$W" merge --no-edit main
echo "merge rc=$?"
git -c safe.directory="$W" log --oneline -2
mkdir -p build/str
CFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"
gcc $CFLAGS -DMSF_BUILD_ID='"parcel-str-scratch"' src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c tests/runner.c tests/sha256.c -o build/str/msf_runner.exe
echo "runner build rc=$?"
gcc $CFLAGS src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c "$S/to_harness.c" -o "$S/to_harness.exe"
echo "harness build rc=$?"
