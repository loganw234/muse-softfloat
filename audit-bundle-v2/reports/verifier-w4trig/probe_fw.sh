#!/bin/bash
# Probe P: firmware targets compile (no flash). Build dir in scratch;
# the copy is read-only source.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:/c/Program Files/CMake/bin:/c/Users/logan/AppData/Local/Microsoft/WinGet/Packages/Ninja-build.Ninja_Microsoft.Winget.Source_8wekyb3d8bbwe:/c/Program Files (x86)/Arm GNU Toolchain arm-none-eabi/14.2 rel1/bin:$PATH"
export PICO_SDK_PATH="C:/Users/logan/pico/pico-sdk"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
rm -rf $V/fwbuild
cmake -S worktrees/verify4-trig/board -B $V/fwbuild -G Ninja \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=OFF > $V/log_fwconfig.txt 2>&1
echo "configure rc=$?"
tail -5 $V/log_fwconfig.txt
cmake --build $V/fwbuild > $V/log_fwbuild.txt 2>&1
echo "build rc=$?"
tail -6 $V/log_fwbuild.txt
grep -c 'FAILED' $V/log_fwbuild.txt
ls $V/fwbuild/*.elf 2>/dev/null
