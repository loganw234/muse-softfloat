#!/usr/bin/env bash
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:/c/Program Files/CMake/bin:/c/Program Files (x86)/Arm GNU Toolchain arm-none-eabi/14.2 rel1/bin:$PATH"
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export MSF_NINJA="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/ninja.exe"
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w-ias15 || exit 9
export IAS15_EXTRACT_DIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/ias15/extract
export IAS15_REF_HASHES=/c/Users/logan/source/repos/Muse-Softfloat/scratch/ias15/out/hashes_native.txt
export IAS15_COMPARE=/c/Users/logan/source/repos/Muse-Softfloat/scratch/ias15/work/compare_hashes.py
bash board/ias15_run.sh
