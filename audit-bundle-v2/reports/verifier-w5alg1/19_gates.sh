#!/usr/bin/env bash
# 19_gates.sh - gates in the copy: smoke + standard (record outcome),
# target-compile of msf_alg.c, type scan, claim surface vs 7c3819c.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
ulimit -v 4194304
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
COPY=$ROOT/worktrees/verify5-alg1
VDIR=$ROOT/scratch/verifier-w5alg1
OUT=$VDIR/out
export MSF_PYTHON=$ROOT/.venv/Scripts/python.exe
export MSF_HOST_CC=/mingw64/bin/gcc
export MSF_ARM_CC="C:/Program Files (x86)/Arm GNU Toolchain arm-none-eabi/14.2 rel1/bin/arm-none-eabi-gcc"
cd "$COPY" || exit 9
echo "=== claim surface: copy HEAD vs parent 7c3819c ==="
git log --oneline -3
git diff --stat 7c3819c HEAD | tail -25
echo "=== board/ untouched? ==="
git diff --name-only 7c3819c HEAD | grep -i "board" || echo "no board/ files in diff"
echo "=== type scan (copy) ==="
if grep -rnwE 'float|double' src include > "$OUT/type_scan.txt" 2>&1; then
  cat "$OUT/type_scan.txt"; echo "TYPE SCAN: DIRTY"
else
  echo "type scan: clean"
fi
echo "=== target-compile msf_alg.c ==="
mkdir -p "$OUT/arm"
"$MSF_ARM_CC" -std=c11 -Os -Wall -Wextra -Werror -mcpu=cortex-m0plus -mthumb \
  -ffreestanding -c src/msf_alg.c -o "$OUT/arm/msf_alg.o" \
  > "$OUT/arm_build.log" 2>&1 && echo "target-compile msf_alg.c: clean" \
  || { cat "$OUT/arm_build.log"; echo "TARGET BUILD FAILED"; }
ls -l "$OUT/arm/msf_alg.o"
echo "=== smoke (expect FAIL; record stage) ==="
tools/run.sh smoke > "$OUT/smoke.log" 2>&1
echo "smoke exit: $?"
grep -E "RUN.SH|FAIL|drift|refused|inventory" "$OUT/smoke.log" | tail -12
cd "$ROOT" || exit 9
