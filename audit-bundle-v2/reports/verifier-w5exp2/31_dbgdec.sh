#!/usr/bin/env bash
# 31_dbgdec.sh - debug the independent decider on the tie cell.
set -u
D="$(dirname "$0")"
gcc -std=c11 -O2 -I"$D" "$D/dbgdec.c" "$D/mydecider.c" -lmpfr -lgmp -o "$D/build/dbgdec.exe"
"$D/build/dbgdec.exe" 2>&1 | tee "$D/31_dbgdec.log"
