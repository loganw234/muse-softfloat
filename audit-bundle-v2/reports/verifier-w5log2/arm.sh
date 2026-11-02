#!/usr/bin/env bash
# arm.sh - target compile at BOTH -Os AND -O3, symbol scan.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
ARM_CC="${MSF_ARM_CC:-arm-none-eabi-gcc}"
ulimit -v 4194304
cd "$SCR" || exit 9
command -v "$ARM_CC" > /dev/null 2>&1 || { echo "ARM CC not found"; exit 2; }
"$ARM_CC" --version | head -1
SRC="msf16.c msf32.c msf64.c msf_flags.c msf_wide.c msf_roundpack.c msf_string.c msf_math.c msf_alg.c"
for opt in Os O3; do
  mkdir -p "build/arm-$opt"
  ok=1
  for f in $SRC; do
    "$ARM_CC" -std=c11 "-$opt" -Wall -Wextra -Werror -mcpu=cortex-m0plus \
      -mthumb -ffreestanding -I"$COPY/include" -I"$COPY/src" \
      -c "$COPY/src/$f" -o "build/arm-$opt/${f%.c}.o" \
      > "logs/arm-$opt.log" 2>&1 || { ok=0; break; }
  done
  if [ $ok -eq 1 ]; then
    echo "target -$opt: CLEAN"
    ls -la "build/arm-$opt/msf_math.o"
  else
    echo "target -$opt: DIRTY"
    tail -5 "logs/arm-$opt.log"
  fi
done
echo "--- symbol scan (Os objects):"
"${ARM_CC%gcc}nm" -u build/arm-Os/*.o 2>/dev/null | sort -u | grep -E ' [A-Za-z_]' > logs/arm-undef.txt || true
cat logs/arm-undef.txt
if grep -Eq '__aeabi_[fd]|__add[sd]f3|__sub[sd]f3|__mul[sd]f3|__div[sd]f3|__truncdfsf2|__extendsfdf2|__float|__fix|__unord|malloc|free|printf' logs/arm-undef.txt; then
  echo "SYMBOL SCAN: refused helper found"
else
  echo "symbol scan: clean"
fi
