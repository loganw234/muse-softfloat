#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
PY=../.venv/Scripts/python.exe
mkdir -p build/board-fw
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
    src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c \
    tests/runner.c tests/sha256.c -o build/board-fw/msf_runner.exe || exit 1
$PY tests/gen_vectors.py board-smoke build/board-fw/board-smoke.vec || exit 1
build/board-fw/msf_runner.exe verify build/board-fw/board-smoke.vec | tail -2
build/board-fw/msf_runner.exe hash build/board-fw/board-smoke.vec | grep whole-run
wc -l < build/board-fw/board-smoke.vec
