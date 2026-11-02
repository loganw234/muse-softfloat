#!/bin/bash
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6ci/dup || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
unset MSF_HOST_CC
gcc -dumpmachine
bash tools/run.sh standard 2>&1 | tail -55
