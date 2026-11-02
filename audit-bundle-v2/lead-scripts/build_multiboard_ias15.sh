#!/usr/bin/env bash
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:/c/Program Files/CMake/bin:/c/Program Files (x86)/Arm GNU Toolchain arm-none-eabi/14.2 rel1/bin:$PATH"
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export MSF_NINJA="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/ninja.exe"
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
source board/common.sh
build_fw ias15fw -DIAS15_EXTRACT_DIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/ias15/extract
mkdir -p build/multiboard-ias15
sha256sum "$BOARD_BUILD/ias15fw/msf_aeabi_selftest.uf2" \
          "$BOARD_BUILD/ias15fw/msf_aeabi_selftest.elf" \
          "$BOARD_BUILD/ias15fw/msf_ias15.uf2" \
          "$BOARD_BUILD/ias15fw/msf_ias15.elf" | tee build/multiboard-ias15/artifacts.sha256
