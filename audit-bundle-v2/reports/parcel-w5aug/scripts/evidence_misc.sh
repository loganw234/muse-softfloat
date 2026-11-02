#!/usr/bin/env bash
set -u
source "$(dirname "$0")/env.sh"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
LOG="$WS/scratch/parcel-w5aug/logs/evidence-misc.log"
: > "$LOG"
failall=0
# vector generator: twice into scratch dirs, byte-stable,
# and byte-identical to the committed copies
for d in gen1 gen2; do
  rm -rf "$WS/scratch/parcel-w5aug/tmp/$d"
  mkdir -p "$WS/scratch/parcel-w5aug/tmp/$d"
  "$MSF_PYTHON" tests/gen_vectors_aug.py "$WS/scratch/parcel-w5aug/tmp/$d" > "$WS/scratch/parcel-w5aug/logs/gen-$d.log" 2>&1 || failall=1
done
for f in aug-f16.vec aug-f32.vec aug-f64.vec; do
  cmp "$WS/scratch/parcel-w5aug/tmp/gen1/$f" "$WS/scratch/parcel-w5aug/tmp/gen2/$f" || failall=1
  cmp "$WS/scratch/parcel-w5aug/tmp/gen1/$f" "tests/vectors/$f" || failall=1
done
sha256sum tests/vectors/aug-f16.vec tests/vectors/aug-f32.vec tests/vectors/aug-f64.vec > "$WS/scratch/parcel-w5aug/logs/vec.sha"
echo "vec-regen-twice byte-stable cmp rc=$failall" >> "$LOG"
cat "$WS/scratch/parcel-w5aug/logs/vec.sha" >> "$LOG"
# target compile: every core TU at -Os and -O3 (arm)
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
for opt in -Os -O3; do
  mkdir -p "build/aug-arm$opt"
  ok=1
  for f in $SRC; do
    arm-none-eabi-gcc -std=c11 "$opt" -Wall -Wextra -Werror -mcpu=cortex-m0plus -mthumb -ffreestanding -ffp-contract=off -c "$f" -o "build/aug-arm$opt/$(basename "$f" .c).o" >> "$WS/scratch/parcel-w5aug/logs/arm$opt.log" 2>&1 || ok=0
  done
  echo "arm target-compile $opt ok=$ok" >> "$LOG"
  [ $ok -eq 1 ] || failall=1
done
arm-none-eabi-gcc --version | head -1 >> "$LOG"
# host strict compile of the harness translation unit is
# covered by run.sh (runner build); board firmware is a
# separate build-only script (no flashing in this parcel).
cat "$LOG"
exit $failall
