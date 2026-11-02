#!/bin/bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6ci/dup || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export MSF_HOST_CC=/c/msys64/mingw64/bin/gcc
bash tools/run.sh standard 2>&1 | tail -55
