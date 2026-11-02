#!/usr/bin/env bash
# Probe 3d: build MSVC ASan runner + aug harness, run unit + full VECS +
# standard extras + aug pool + corrupt control under real ASan.
set -u
cd "$(dirname "$0")/.." || exit 9
ROOT=$PWD
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
PY="$MSF_PYTHON"
{
echo "===== MSVC build (bat) ====="
T0=$(date +%s)
MSYS2_ARG_CONV_EXCL='*' /c/Windows/System32/cmd.exe /c "$(cygpath -w "$ROOT/scripts/msvc_build.bat")" > "$ROOT/logs/12_msvc_build.log" 2>&1
echo "bat rc=$? dt=$(($(date +%s)-T0))s — build log summary:"
grep -E 'Version|exit=|error|Error' "$ROOT/logs/12_msvc_build.log" | head -20
echo
echo "===== ASan runs (runtime DLL dir on PATH) ====="
export PATH="/c/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/MSVC/14.51.36231/bin/Hostx64/x64:$PATH"
cd tree || exit 8
T0=$(date +%s)
$PY ../scripts/verify_driver.py "$(cygpath -w "$PWD")" "$(cygpath -w "$PWD/build-san/msvc/msf_runner_asan.exe")" msvc-asan "$(cygpath -w "$ROOT/logs/13_asan_verify.log")"
echo "driver rc=$? dt=$(($(date +%s)-T0))s"
echo
echo "===== ASan: standard extras ====="
T0=$(date +%s)
./build-san/msvc/msf_runner_asan.exe verify "build-san/f16-exhaustive.vec" "build-san/pack-sweep.vec" > build-san/verify-extras-asan.log 2>&1
echo "asan extras rc=$? dt=$(($(date +%s)-T0))s"
grep -E '^(total|VERDICT)|AddressSanitizer|ERROR' build-san/verify-extras-asan.log | head -10
echo
echo "===== ASan: aug pool ====="
T0=$(date +%s)
./build-san/msvc/aug_exhaustive_asan.exe pool > build-san/aug-pool-asan.log 2>&1
echo "asan aug pool rc=$? dt=$(($(date +%s)-T0))s"
grep -E '^(aug_exhaustive|  kind|VERDICT)|AddressSanitizer|ERROR' build-san/aug-pool-asan.log | head -14
echo
echo "===== ASan: corrupt control must be refused ====="
./build-san/msvc/msf_runner_asan.exe verify build-san/corrupt.vec > build-san/corrupt-asan.log 2>&1
echo "corrupt-vs-asan rc=$? (must be nonzero)"
grep -E 'VERDICT' build-san/corrupt-asan.log | head -2
} > "$ROOT/logs/12_msvc_run.log" 2>&1
cat "$ROOT/logs/12_msvc_run.log"
