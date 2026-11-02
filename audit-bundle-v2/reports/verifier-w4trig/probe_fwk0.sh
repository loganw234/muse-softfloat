#!/bin/bash
# Probe P2: keep-going firmware build to enumerate ALL failures.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:/c/Program Files/CMake/bin:/c/Users/logan/AppData/Local/Microsoft/WinGet/Packages/Ninja-build.Ninja_Microsoft.Winget.Source_8wekyb3d8bbwe:/c/Program Files (x86)/Arm GNU Toolchain arm-none-eabi/14.2 rel1/bin:$PATH"
export PICO_SDK_PATH="C:/Users/logan/pico/pico-sdk"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
cmake --build $V/fwbuild -- -k 0 > $V/log_fwbuild_k0.txt 2>&1
echo "keep-going rc=$?"
grep -c '^FAILED' $V/log_fwbuild_k0.txt
grep '^FAILED' $V/log_fwbuild_k0.txt | sed 's|.*/||' | sort | uniq -c | head
grep -E 'error:' $V/log_fwbuild_k0.txt | sort | uniq -c | head
