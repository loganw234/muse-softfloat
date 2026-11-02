#!/usr/bin/env bash
# 19b_standard.sh - record standard outcome + smoke gen.log cause.
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
echo "=== smoke drift cause ==="
cat build/smoke/gen.log
echo "=== standard (expect FAIL; record stage) ==="
tools/run.sh standard > "$OUT/standard.log" 2>&1
echo "standard exit: $?"
grep -E "RUN.SH" "$OUT/standard.log" | tail -3
cd "$ROOT" || exit 9
