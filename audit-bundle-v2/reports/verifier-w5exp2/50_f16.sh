#!/usr/bin/env bash
# 50_f16.sh - LEG f16: exhaustive binary16 x 2 funcs x 5 modes vs own decider.
set -u
D="$(dirname "$0")"
ulimit -v 4194304
START=$(date +%s)
"$D/build/vdriver.exe" f16 2>&1 | tee "$D/50_f16.log"
echo "wall $(( $(date +%s) - START ))s" | tee -a "$D/50_f16.log"
