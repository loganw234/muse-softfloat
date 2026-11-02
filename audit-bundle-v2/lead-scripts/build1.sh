#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=$PWD/../scratch/lead/tmp
mkdir -p "$TMPDIR" build/host
export TMP="$(cygpath -w "$TMPDIR")" TEMP="$(cygpath -w "$TMPDIR")"
echo "dumpmachine: $(gcc -dumpmachine)"
cat > build/host/probe.c <<'EOF'
#include <stdio.h>
int main(void){ printf("FLT_EVAL_METHOD=%d\n", __FLT_EVAL_METHOD__); return __FLT_EVAL_METHOD__ == 0 ? 0 : 1; }
EOF
gcc -std=c11 build/host/probe.c -o build/host/probe.exe && ./build/host/probe.exe; echo "probe rc=$?"
CFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"
BUILD_ID="host-$(gcc -dumpmachine)-gcc$(gcc -dumpversion)"
gcc $CFLAGS -DMSF_BUILD_ID="\"$BUILD_ID\"" src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c tests/runner.c tests/sha256.c -o build/host/msf_runner.exe
echo "build rc=$?"
./build/host/msf_runner.exe unit; echo "unit rc=$?"
./build/host/msf_runner.exe verify tests/vectors/*.vec > build/host/verify.log 2>&1; echo "verify rc=$?"
tail -15 build/host/verify.log
grep -c '^FAIL' build/host/verify.log || true
head -5 build/host/verify.log
