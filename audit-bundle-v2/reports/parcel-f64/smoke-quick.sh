#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/w1/tmp build/smoke
export TMPDIR=$PWD/build/w1/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
PY=../../.venv/Scripts/python.exe
export MSF_TESTFLOAT_GEN='C:\Users\logan\source\repos\Muse-Softfloat\scratch\oracles\TestFloat-3e\build\Linux-x86_64-GCC\testfloat_gen.exe'
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c"
echo "build runner"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -DMSF_BUILD_ID='"w1-f64-quick"' $SRC tests/runner.c tests/sha256.c -o build/smoke/msf_runner.exe > build/w1/runner-build.log 2>&1
rc=$?; cat build/w1/runner-build.log; echo "build rc=$rc"; [ $rc -eq 0 ] || exit $rc
build/smoke/msf_runner.exe unit > build/w1/unit.log 2>&1; echo "unit rc=$?"; tail -20 build/w1/unit.log
# quick berkeley add te level1 take 20000
$PY tests/berkeley_ingest.py --fn f64_add --rm te --level 1 --take 20000 --out build/w1/quick-add.vec > build/w1/quick-add-ingest.log 2>&1
echo "ingest rc=$?"; cat build/w1/quick-add-ingest.log
build/smoke/msf_runner.exe verify build/w1/quick-add.vec > build/w1/quick-add-verify.log 2>&1
echo "verify rc=$?"; grep -E '^(file|prov|total|VERDICT|FAIL)' build/w1/quick-add-verify.log | head -40
