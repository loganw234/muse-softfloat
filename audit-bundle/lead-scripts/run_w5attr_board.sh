#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
WS="$(cd .. && pwd)"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export TMPDIR="$WS/scratch/lead/tmp" TMP="$WS/scratch/lead/tmp" TEMP="$WS/scratch/lead/tmp"
export MSF_BOARD_SERIAL=E66440A2CB6F5C2B
export MSF_BOARD_PORT=COM8
mkdir -p "$TMPDIR"
echo "lead board target: serial=$MSF_BOARD_SERIAL port=$MSF_BOARD_PORT"
bash tools/run.sh board > build/w5attr-board.log 2>&1; rc=$?
cat build/w5attr-board.log
echo "board rc=$rc"
exit $rc
