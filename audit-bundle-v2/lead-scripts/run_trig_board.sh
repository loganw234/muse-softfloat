#!/usr/bin/env bash
# Lead board sampled replay after the Step 2c merge (genuine board only).
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export MSF_BOARD_SERIAL=E66440A2CB6F5C2B
export MSF_BOARD_PORT=COM8
echo "lead board target: serial=$MSF_BOARD_SERIAL port=$MSF_BOARD_PORT"
export TMPDIR="$PWD/build/tmp" TMP="$PWD/build/tmp" TEMP="$PWD/build/tmp"
mkdir -p "$TMPDIR"
LOG=/c/Users/logan/source/repos/Muse-Softfloat/scratch/lead/w4-trig-board.log
bash tools/run.sh board > "$LOG" 2>&1
rc=$?
echo "run.sh board rc=$rc log=$LOG"
grep -E '^(== budget|board lock|target compiler|built firmware|flashing|flash target|replay port|board:|host:|board replay|hello|HELLO|UART|budget board|RUN\.SH)' "$LOG" || true
tail -8 "$LOG"
exit $rc
