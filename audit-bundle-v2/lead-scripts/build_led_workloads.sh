#!/usr/bin/env bash
set -u
WS="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$WS/muse-softfloat" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/c/msys64/mingw64/bin:/c/msys64/usr/bin:/usr/bin:$PATH"
export MSF_PYTHON="../.venv/Scripts/python.exe"
source board/common.sh
build_fw ias15fw -DIAS15_EXTRACT_DIR="$WS/scratch/ias15/extract"
build_fw kissfftfw -DMSF_KISSFFT_DIR="$WS/scratch/parcel-w4kissfft/tree"
ls -la "$BOARD_BUILD/ias15fw/msf_ias15.uf2" "$BOARD_BUILD/ias15fw/msf_aeabi_selftest.uf2" "$BOARD_BUILD/kissfftfw/msf_kissfft.uf2"
