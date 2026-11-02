#!/usr/bin/env bash
# Probe 1d: MSVC ASan canaries + mingw trap-UBSan vs runtime-sized heap.
set -u
cd "$(dirname "$0")/.." || exit 9
mkdir -p logs tmp canary/bin
export TMPDIR=$PWD/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
GCC=/c/msys64/mingw64/bin/gcc
{
echo "===== mingw trap-UBSan vs heap_dyn (runtime alloc size) ====="
$GCC -std=c11 -O1 -g -fsanitize=undefined -fsanitize-undefined-trap-on-error -fno-sanitize-recover=all canary/heap_dyn.c -o canary/bin/trap-heap_dyn.exe 2>&1
echo "build exit=$?"
"$MSF_PYTHON" scripts/run_canary.py "$(cygpath -w "$PWD/canary/bin")\\trap-heap_dyn.exe|8|64"
echo
echo "===== MSVC ASan canaries (bat, one stream) ====="
cmd //c "$(cygpath -w "$PWD/scripts/msvc_canary.bat")"
echo "bat exit=$?"
} > logs/05_msvc_and_dyn.log 2>&1
cat logs/05_msvc_and_dyn.log
