#!/usr/bin/env bash
# wv_oracle_build.sh - compile pinned SoftFloat-3e sources into scratch objects.
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1prep/tmp
export TMP=$TMPDIR
export TEMP=$TMPDIR
SRC=/c/Users/logan/source/repos/Muse-Softfloat/scratch/oracles/SoftFloat-3e/source
BLD=/c/Users/logan/source/repos/Muse-Softfloat/scratch/oracles/SoftFloat-3e/build/Linux-x86_64-GCC
OUT=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1prep/oracle
mkdir -p "$OUT"
cd "$SRC" || exit 9
n=0
bad=0
for f in *.c 8086-SSE/*.c; do
  base=$(echo "$f" | tr '/' '_')
  if ! gcc -pipe -O1 -DSOFTFLOAT_FAST_INT64 -DSOFTFLOAT_ROUND_ODD -DINLINE_LEVEL=5 -DSOFTFLOAT_FAST_DIV32TO16 -DSOFTFLOAT_FAST_DIV64TO32 -I"$BLD" -I. -I8086-SSE -Iinclude -c "$f" -o "$OUT/$base.o" 2>"$OUT/$base.err"; then
    echo "FAIL $f"
    bad=$((bad+1))
  fi
  n=$((n+1))
done
echo "compiled=$n bad=$bad"
