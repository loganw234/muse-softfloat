#!/usr/bin/env bash
# arm.sh - verifier-w5aug: target-compile the copy's sources with
# arm-none-eabi-gcc at -Os AND -O3 (read-only w.r.t. the copy).
set -u
cd "$(dirname "$0")" || exit 9
COPY=../../worktrees/verify5-aug
ARM_CC="${MSF_ARM_CC:-arm-none-eabi-gcc}"
ulimit -v 3000000 2>/dev/null || true
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
fail() { echo "ARM.SH: FAIL - $1"; exit 1; }
command -v "$ARM_CC" >/dev/null 2>&1 || fail "$ARM_CC not found"
echo "target compiler: $("$ARM_CC" --version | head -1)"
for opt in Os O3; do
  mkdir -p "build/arm-$opt"
  for f in $SRC; do
    "$ARM_CC" -std=c11 -$opt -Wall -Wextra -Werror -mcpu=cortex-m0plus -mthumb \
      -ffreestanding -I"$COPY/include" -c "$COPY/$f" \
      -o "build/arm-$opt/$(basename "$f" .c).o" > build/arm-$opt.log 2>&1 \
      || { cat build/arm-$opt.log; fail "target -$opt build failed: $f"; }
  done
  echo "target -$opt: clean (10 objects)"
  ${ARM_CC%gcc}nm -u "build/arm-$opt"/*.o 2>/dev/null | sort -u | grep -E ' [A-Za-z_]' \
    > "build/arm-$opt-undefined.txt" || true
  echo "undefined at -$opt ($(wc -l < "build/arm-$opt-undefined.txt")):"
  cat "build/arm-$opt-undefined.txt"
  if grep -Eq '__aeabi_[fd]|__add[sd]f3|__sub[sd]f3|__mul[sd]f3|__div[sd]f3|__truncdfsf2|__extendsfdf2|__float|__fix|__unord|malloc|free|printf' \
      "build/arm-$opt-undefined.txt"; then
    fail "forbidden helper symbol at -$opt (SF-0 5.3)"
  fi
  echo "symbol scan at -$opt: clean"
done
echo ARM.SH: OK
