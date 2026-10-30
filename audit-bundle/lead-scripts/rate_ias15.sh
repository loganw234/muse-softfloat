#!/usr/bin/env bash
# IAS15 step-rate measurement at reduced block (T 200): the scripted
# T 2000 exceeded the host's 600 s idle timeout (firmware prints
# only at block end). Board still carries msf_ias15 from the main run.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:/c/Program Files/CMake/bin:/c/Program Files (x86)/Arm GNU Toolchain arm-none-eabi/14.2 rel1/bin:$PATH"
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export MSF_NINJA="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/ninja.exe"
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w-ias15 || exit 9
IAS15_LEDGER_DIR="$(cd ../../ledger && pwd)"
source board/common.sh
LEDGER_DIR="$IAS15_LEDGER_DIR"
LOCK="$LEDGER_DIR/board.lock"
take_lock "IAS15 rate measurement T200 (follow-up to COMPARE PASS run)"
"$PY" board/ias15_host.py --cmd "T 200" 2>&1 | tee build/ias15-board/rate200.log
echo "rate capture done"
