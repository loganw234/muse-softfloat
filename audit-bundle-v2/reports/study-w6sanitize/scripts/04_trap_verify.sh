#!/usr/bin/env bash
# Probe 1c: re-verify trap-on-error canaries with a Python runner
# (true Windows exit codes), MSVC via vswhere, pacman install route.
# Single-stream log write (host offset-0 append bug: no >> loops).
set -u
cd "$(dirname "$0")/.." || exit 9
mkdir -p logs tmp canary/bin
export TMPDIR=$PWD/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
PY="$MSF_PYTHON"
GCC=/c/msys64/mingw64/bin/gcc
{
echo "===== trap-on-error canaries via python runner ====="
echo "python: $($PY --version 2>&1)"
for prog in clean heap ub ub_shift; do
  $GCC -std=c11 -O1 -g -fsanitize=undefined -fsanitize-undefined-trap-on-error -fno-sanitize-recover=all "canary/${prog}.c" -o "canary/bin/trap-${prog}.exe" 2>&1
  echo "built trap-${prog}.exe (gcc exit $?)"
done
WINBIN="$(cygpath -w "$PWD/canary/bin")"
$PY scripts/run_canary.py \
  "$WINBIN\\trap-clean.exe" \
  "$WINBIN\\trap-heap.exe|64" \
  "$WINBIN\\trap-ub.exe" \
  "$WINBIN\\trap-ub_shift.exe|40" \
  "$WINBIN\\mingw64-none-clean.exe" \
  "$WINBIN\\mingw64-none-heap.exe|64" \
  "$WINBIN\\mingw64-none-ub.exe"
echo
echo "===== same binaries, bash-native exit (for contrast) ====="
./canary/bin/trap-ub.exe; echo "bash sees trap-ub exit=$?"
./canary/bin/trap-ub_shift.exe 40; echo "bash sees trap-ub_shift exit=$?"
echo
echo "===== MSVC via vswhere ====="
VSWHERE="/c/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe"
if [ -x "$VSWHERE" ]; then
  echo "installations:"
  "$VSWHERE" -all -products '*' -property installationPath 2>&1
  echo "cl.exe find:"
  "$VSWHERE" -latest -products '*' -find 'VC\Tools\MSVC\*\bin\Hostx64\x64\cl.exe' 2>&1
  echo "(end cl find)"
else
  echo "vswhere absent"
fi
echo
echo "===== pacman install-route packages (local sync db) ====="
pacman -Si mingw-w64-clang-x86_64-clang 2>&1 | grep -E '^(Name|Version|Download Size|Installed Size)' || true
pacman -Si mingw-w64-clang-x86_64-compiler-rt 2>&1 | grep -E '^(Name|Version|Download Size|Installed Size)' || true
pacman -Si mingw-w64-x86_64-compiler-rt 2>&1 | grep -E '^(Name|Version|Download Size|Installed Size)' || true
pacman -Si mingw-w64-ucrt-x86_64-clang 2>&1 | grep -E '^(Name|Version|Download Size|Installed Size)' || true
} > logs/04_trap_verify.log 2>&1
cat logs/04_trap_verify.log
