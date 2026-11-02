#!/usr/bin/env bash
# 33_dbgdec3.sh - exact values through recipe steps.
set -u
D="$(dirname "$0")"
gcc -std=c11 -O2 -I"$D" "$D/dbgdec3.c" -lmpfr -lgmp -o "$D/build/dbgdec3.exe"
"$D/build/dbgdec3.exe" 2>&1 | tee "$D/33_dbgdec3.log"
