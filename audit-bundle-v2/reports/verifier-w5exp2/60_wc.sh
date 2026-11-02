#!/usr/bin/env bash
# 60_wc.sh - LEG f64: 100% published worst-case inputs, both funcs x 5 modes.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
ORACLE="$ROOT/scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94"
E2="$ORACLE/src/binary64/exp2/exp2.wc"
EM1="$ORACLE/src/binary64/exp2m1/exp2m1.wc"
{
echo "== wc input hashes (pinned Step 0b tree, read-only) =="
sha256sum "$E2" "$EM1"
ls -la "$E2" "$EM1"
} 2>&1 | tee "$D/60_wc_hashes.log"
ulimit -v 4194304
START=$(date +%s)
"$D/build/vdriver.exe" wc exp2 "$E2" 2>&1 | tee "$D/60_wc_exp2.log"
"$D/build/vdriver.exe" wc exp2m1 "$EM1" 2>&1 | tee "$D/60_wc_exp2m1.log"
echo "wall $(( $(date +%s) - START ))s" | tee -a "$D/60_wc_exp2m1.log"
