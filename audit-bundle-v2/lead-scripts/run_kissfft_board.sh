#!/usr/bin/env bash
# Lead board run: KissFFT Fork B bit-identity, genuine board, serial-targeted.
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
WS="$(cd .. && pwd)"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export TMPDIR="$WS/scratch/lead/tmp" TMP="$WS/scratch/lead/tmp" TEMP="$WS/scratch/lead/tmp"
export MSF_KISSFFT_DIR="$WS/scratch/parcel-w4kissfft/tree"
export KISSFFT_EXPECT="$WS/scratch/parcel-w4kissfft/out/hashes-main.txt"
export MSF_BOARD_SERIAL=E66440A2CB6F5C2B
export MSF_BOARD_PORT=COM8
mkdir -p "$TMPDIR" build
bash board/kissfft_run.sh > build/kissfft-board-run.log 2>&1; rc=$?
cat build/kissfft-board-run.log
echo "kissfft_board rc=$rc"
exit $rc
