#!/usr/bin/env bash
# Probe 1e: MSVC canaries via real cmd.exe; trap-UBSan boundary canary.
set -u
cd "$(dirname "$0")/.." || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
GCC=/c/msys64/mingw64/bin/gcc
mkdir -p logs tmp canary/bin
export TMPDIR=$PWD/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
{
echo "===== mingw trap-UBSan vs heap_far (size lost across call) ====="
$GCC -std=c11 -O1 -g -fsanitize=undefined -fsanitize-undefined-trap-on-error -fno-sanitize-recover=all canary/heap_far.c -o canary/bin/trap-heap_far.exe 2>&1
echo "build exit=$?"
"$MSF_PYTHON" scripts/run_canary.py "$(cygpath -w "$PWD/canary/bin")\\trap-heap_far.exe|8|64"
echo
echo "===== MSVC ASan canaries via System32 cmd.exe ====="
MSYS2_ARG_CONV_EXCL='*' /c/Windows/System32/cmd.exe /c "$(cygpath -w "$PWD/scripts/msvc_canary.bat")"
echo "bat exit=$?"
} > logs/06_msvc_retry.log 2>&1
cat logs/06_msvc_retry.log
