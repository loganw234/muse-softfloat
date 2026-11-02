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
CFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"
gcc $CFLAGS src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c "$S/to_harness.c" -o "$S/to_harness.exe"
echo "harness build rc=$?"
R=build/str/msf_runner.exe
date '+rerun start %H:%M:%S'
"$R" verify tests/vectors/from-decimal-str.vec tests/vectors/from-hex-str.vec tests/vectors/to-decimal-str.vec tests/vectors/to-hex-str.vec > "$S/directed2.log" 2>&1
echo "directed rc=$?"
grep -E '^(file|total|VERDICT)' "$S/directed2.log"
grep '^FAIL' "$S/directed2.log" | head -10
"$R" verify "$S/bulk/to-decimal-700k.vec" > "$S/bulk-to-dec2.log" 2>&1
echo "bulk to-dec rc=$?"
grep -E '^(file|total|VERDICT)' "$S/bulk-to-dec2.log"
grep '^FAIL' "$S/bulk-to-dec2.log" | head -10
"$R" verify "$S/bulk/to-hex-300k.vec" > "$S/bulk-to-hex2.log" 2>&1
echo "bulk to-hex rc=$?"
grep -E '^(file|total|VERDICT)' "$S/bulk-to-hex2.log"
grep '^FAIL' "$S/bulk-to-hex2.log" | head -10
"$R" verify "$S/bulk/f16-exhaustive.vec" > "$S/bulk-f16exh.log" 2>&1
echo "f16 exhaustive rc=$?"
grep -E '^(file|total|VERDICT)' "$S/bulk-f16exh.log"
grep '^FAIL' "$S/bulk-f16exh.log" | head -10
"$S/to_harness.exe" rt > "$S/roundtrips.log" 2>&1
echo "harness rt rc=$?"
cat "$S/roundtrips.log"
date '+rerun done %H:%M:%S'
