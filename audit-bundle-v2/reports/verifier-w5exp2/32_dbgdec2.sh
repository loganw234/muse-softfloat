#!/usr/bin/env bash
# 32_dbgdec2.sh - stepwise replicate of the decider path.
set -u
D="$(dirname "$0")"
gcc -std=c11 -O2 -I"$D" "$D/dbgdec2.c" -lmpfr -lgmp -o "$D/build/dbgdec2.exe"
"$D/build/dbgdec2.exe" 2>&1 | tee "$D/32_dbgdec2.log"
