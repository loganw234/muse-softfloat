#!/usr/bin/env bash
# verifier second-attempt: type scan + target -Os/-O3 builds, sizes recorded.
set -u
cd /mnt/c/Users/logan/source/repos/Muse-Softfloat
C=worktrees/verify5-exp2
O=scratch/verifier-w5exp2/smoke
ARM="/mnt/c/Program Files (x86)/Arm GNU Toolchain arm-none-eabi/14.2 rel1/bin/arm-none-eabi-gcc.exe"
echo "--- type scan (must be empty) ---"
if grep -rnwE 'float|double' "$C/src" "$C/include" > "$O/type-scan.txt" 2>&1; then
  cat "$O/type-scan.txt"; echo "TYPE SCAN: DIRTY"
else
  echo "type scan: clean"
fi
echo "--- target builds ---"
"$ARM" --version | head -1
mkdir -p "$O/arm-Os" "$O/arm-O3"
for opt in Os O3; do
  for f in src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c; do
    b=$(basename "$f" .c)
    "$ARM" -std=c11 "-$opt" -Wall -Wextra -Werror -mcpu=cortex-m0plus -mthumb -ffreestanding \
      -I "$C/include" -c "$C/$f" -o "$O/arm-$opt/$b.o" >> "$O/target-$opt.log" 2>&1 \
      || { echo "TARGET -$opt BUILD FAILED: $f"; tail -15 "$O/target-$opt.log"; exit 1; }
  done
  echo "target -$opt: build clean"
done
echo "--- msf_math.o sizes ---"
ls -l "$O/arm-Os/msf_math.o" "$O/arm-O3/msf_math.o"
echo "--- host -O2/-O3 (parcel probe) ---"
gcc -std=c11 -O2 -Wall -Wextra -Werror -I "$C/include" -c "$C/src/msf_math.c" -o "$O/math-O2.o" 2>&1 | head -5
gcc -std=c11 -O3 -Wall -Wextra -Werror -I "$C/include" -c "$C/src/msf_math.c" -o "$O/math-O3.o" 2>&1 | head -5
echo "host builds done"
