#!/usr/bin/env bash
# s12_target.sh - target-compile gate under the project's exact flags,
# then informational sizes (relaxed flags, never quoted as a gate).
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR="$(pwd)/scratch/verifier-w5alg2/tmp"
export TMP="$TMPDIR" TEMP="$TMPDIR"
mkdir -p "$TMPDIR" scratch/verifier-w5alg2/out
ulimit -v 2097152
OUT=scratch/verifier-w5alg2/out
COPY=worktrees/verify5-alg2
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
{
rm -rf "$TMPDIR/arm" && mkdir -p "$TMPDIR/arm"
echo "--- gate: exact project flags (-Werror) ---"
gate_fail=0
for f in $SRC; do
  arm-none-eabi-gcc -std=c11 -Os -Wall -Wextra -Werror -mcpu=cortex-m0plus -mthumb -ffreestanding -c "$COPY/$f" -o "$TMPDIR/arm/$(basename $f .c).o" > "$TMPDIR/arm-build.log" 2>&1 || gate_fail=1
done
echo "gate rc=$([ $gate_fail -eq 0 ] && echo 0 || echo 1)"
grep -E "error|warning" "$TMPDIR/arm-build.log" | head -8
echo "--- info: relaxed flags for sizes ---"
rm -rf "$TMPDIR/arm-relaxed" && mkdir -p "$TMPDIR/arm-relaxed"
for f in $SRC; do
  arm-none-eabi-gcc -std=c11 -Os -Wall -mcpu=cortex-m0plus -mthumb -ffreestanding -fstack-usage -c "$COPY/$f" -o "$TMPDIR/arm-relaxed/$(basename $f .c).o" >> "$TMPDIR/arm-relaxed-build.log" 2>&1 || echo "RELAXED FAIL $f"
done
arm-none-eabi-size "$TMPDIR/arm-relaxed/msf_alg.o"
arm-none-eabi-nm --print-size --size-sort "$TMPDIR/arm-relaxed/msf_alg.o" | grep -E "hypot|rsqrt" | head -8
grep -H "hypot_core" "$TMPDIR/arm-relaxed/"*.su
arm-none-eabi-nm -u "$TMPDIR/arm-relaxed/"*.o | sort -u | grep -E " [A-Za-z]" | head -12
} 2>&1 | tee $OUT/s12_target.log
