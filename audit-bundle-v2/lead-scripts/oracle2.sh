#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/oracles || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=$PWD/tmp
mkdir -p "$TMPDIR"
export TMP="$(cygpath -w "$TMPDIR")" TEMP="$(cygpath -w "$TMPDIR")"
echo "TMPDIR=[$TMPDIR] TMP=[$TMP] TEMP=[$TEMP]"
ls -ld "$TMPDIR"
echo x > "$TMPDIR/probe.txt" && echo "tmp writable"
echo "gcc: $(gcc -dumpmachine) $(gcc -dumpversion); make: $(make --version | head -1)"
gcc -c -x c -o /dev/null - <<'EOF'
int main(void){return 0;}
EOF
echo "stdin compile rc=$?"
grep -E 'SOFTFLOAT|COMPILE_C|LINK' TestFloat-3e/build/Linux-x86_64-GCC/Makefile | head -20
echo ---BUILD-SOFTFLOAT---
cd SoftFloat-3e/build/Linux-x86_64-GCC || exit 9
make > ../../../sf-build.log 2>&1
echo "softfloat build rc=$?"
tail -3 ../../../sf-build.log
ls -la softfloat.a 2>/dev/null || ls
