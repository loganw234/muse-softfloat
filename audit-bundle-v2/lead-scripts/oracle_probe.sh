#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/oracles || exit 9
which -a make
ls /usr/bin/make* 2>/dev/null
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=$PWD/tmp
export TMP="$(cygpath -w "$TMPDIR")" TEMP="$(cygpath -w "$TMPDIR")"
cd SoftFloat-3e/build/Linux-x86_64-GCC || exit 9
echo "--- direct gcc (same command make ran) ---"
gcc -c -Werror-implicit-function-declaration -DSOFTFLOAT_FAST_INT64 -DSOFTFLOAT_ROUND_ODD -DINLINE_LEVEL=5 -DSOFTFLOAT_FAST_DIV32TO16 -DSOFTFLOAT_FAST_DIV64TO32 -I. -I../../source/8086-SSE -I../../source/include -O2 -o s_eq128.o ../../source/s_eq128.c; echo "direct rc=$?"
echo "--- env make single target ---"
env TMPDIR="$TMPDIR" TMP="$TMP" TEMP="$TEMP" make s_le128.o; echo "envmake rc=$?"
echo "--- env seen by a make recipe ---"
printf 'show:\n\t@echo TMPDIR=[%s] TMP=[%s]\n\t@printenv | grep -i tmp || true\n' '$(TMPDIR)' '$(TMP)' > /tmp/show.mk
make -f /tmp/show.mk show
