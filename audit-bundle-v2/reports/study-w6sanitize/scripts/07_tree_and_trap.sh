#!/usr/bin/env bash
# Probe 3a: copy tree at repo HEAD via git archive; build gate-flags twin
# and trap-UBSan twin; run unit + full VECS verify under trap-UBSan.
set -u
cd "$(dirname "$0")/.." || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
PY="$MSF_PYTHON"
mkdir -p logs tmp
export TMPDIR=$PWD/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
REPO_WIN='C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat'
{
echo "===== copy tree via git archive HEAD ====="
git -c safe.directory="$REPO_WIN" -C "$REPO_WIN" rev-parse HEAD
rm -rf tree tree.tar
git -c safe.directory="$REPO_WIN" -C "$REPO_WIN" archive -o "$PWD/tree.tar" HEAD
echo "archive exit=$?"
sha256sum tree.tar
mkdir -p tree
tar -xf tree.tar -C tree
echo "tree files: $(find tree -type f | wc -l)"
ls tree
echo
echo "===== builds (in copied tree) ====="
cd tree || exit 8
HOST_CC=gcc
echo "host compiler: $($HOST_CC -dumpmachine) $($HOST_CC -dumpversion)"
CFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
mkdir -p build-san/tmp
export TMPDIR=$PWD/build-san/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
ID="host-$($HOST_CC -dumpmachine)-gcc$($HOST_CC -dumpversion)"
T0=$(date +%s)
$HOST_CC $CFLAGS -DMSF_BUILD_ID="\"$ID\"" $SRC tests/runner.c tests/sha256.c -o build-san/msf_runner_base.exe > build-san/build-base.log 2>&1
echo "baseline build rc=$? dt=$(($(date +%s)-T0))s"
head -5 build-san/build-base.log
T0=$(date +%s)
$HOST_CC $CFLAGS -fsanitize=undefined -fsanitize-undefined-trap-on-error -fno-sanitize-recover=all -DMSF_BUILD_ID="\"$ID-trapubsan-study\"" $SRC tests/runner.c tests/sha256.c -o build-san/msf_runner_trap.exe > build-san/build-trap.log 2>&1
echo "trap-UBSan build rc=$? dt=$(($(date +%s)-T0))s"
head -5 build-san/build-trap.log
ls -la build-san/*.exe
echo
echo "===== trap-UBSan: unit + full VECS verify ====="
$PY ../scripts/verify_driver.py "$(cygpath -w "$PWD")" "$(cygpath -w "$PWD/build-san/msf_runner_trap.exe")" trap-ubsan "$(cygpath -w "$PWD/../logs/08_trap_verify.log")"
echo "driver rc=$?"
} > logs/07_tree_and_trap.log 2>&1
tail -70 logs/07_tree_and_trap.log
