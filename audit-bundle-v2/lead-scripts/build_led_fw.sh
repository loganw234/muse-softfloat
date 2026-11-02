#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/c/msys64/mingw64/bin:/c/msys64/usr/bin:/usr/bin:$PATH"
export MSF_PYTHON="../.venv/Scripts/python.exe"
source board/common.sh
build_fw fw
ls -la "$BOARD_BUILD/fw"/*.uf2
