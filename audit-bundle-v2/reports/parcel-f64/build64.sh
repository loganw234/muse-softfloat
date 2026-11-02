#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/w1/tmp
export TMPDIR=$PWD/build/w1/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
echo "compiler: $(gcc -dumpmachine) $(gcc -dumpversion)"
grep -rnwE 'float|double' src/msf64.c && echo "TYPE WORDS FOUND" || echo "type words: none in msf64.c"
wc -l src/msf64.c
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -c src/msf64.c -o build/w1/msf64.o > build/w1/msf64-build.log 2>&1
rc=$?
cat build/w1/msf64-build.log
echo "build rc=$rc"
if [ $rc -eq 0 ]; then nm build/w1/msf64.o | grep ' T ' | wc -l; nm build/w1/msf64.o | grep ' T msf64_' | head -200; fi
exit $rc
