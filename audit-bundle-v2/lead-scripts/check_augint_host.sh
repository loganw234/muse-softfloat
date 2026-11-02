#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../../worktrees/w6-augint" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/msys64/mingw64/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/build/leadcheck/tmp" TMP="$PWD/build/leadcheck/tmp" TEMP="$PWD/build/leadcheck/tmp"
mkdir -p build/leadcheck/tmp
command -v gcc || echo "NO GCC"
gcc --version | head -n 1
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
    src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c \
    src/msf_roundpack.c src/msf_string.c src/msf_aug.c tests/sha256.c \
    board/interval_workload.c board/interval_host.c \
    -o build/leadcheck/interval_host.exe > build/leadcheck/build.log 2>&1 || { echo "BUILD FAIL"; cat build/leadcheck/build.log; exit 1; }
echo "interval_host link OK"
./build/leadcheck/interval_host.exe tests/interval_catalogue.tsv > build/leadcheck/host.log 2>&1
rc=$?
echo "host rc=$rc"
grep -E "IW1|SHA|rows|SUMMARY" build/leadcheck/host.log | head -n 8
exit $rc
