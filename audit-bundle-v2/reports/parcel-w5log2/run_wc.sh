#!/usr/bin/env bash
# binary64 worst-case legs (100% published sets) + seeded
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT/worktrees/w5-log2"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR="$ROOT/scratch/parcel-w5log2/tmp"
mkdir -p "$TMPDIR"
ulimit -v 4194304 2>/dev/null || true
echo "ulimit -v: $(ulimit -v) KB"
EXE=build/explog/explog_exhaustive.exe
PIN=../../scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94/src/binary64
S="$ROOT/scratch/parcel-w5log2"
echo "=== wc log2 (start $(date '+%H:%M:%S')) ==="
EXPLOG_WC_DUMP="$S/wc-log2-inputs.txt" "$EXE" wc log2 "$PIN/log2/log2.wc" 2>&1 | tee "$S/wc-log2.log"
echo "log2 unique encodings: $(sort -u "$S/wc-log2-inputs.txt" | wc -l) occurrences: $(wc -l < "$S/wc-log2-inputs.txt")"
echo "=== wc log2p1 (start $(date '+%H:%M:%S')) ==="
EXPLOG_WC_DUMP="$S/wc-log2p1-inputs.txt" "$EXE" wc log2p1 "$PIN/log2p1/log2p1.wc" 2>&1 | tee "$S/wc-log2p1.log"
echo "log2p1 unique encodings: $(sort -u "$S/wc-log2p1-inputs.txt" | wc -l) occurrences: $(wc -l < "$S/wc-log2p1-inputs.txt")"
echo "=== f64seed 20261028 x200000 (all4) ==="
"$EXE" f64seed 20261028 200000 2>&1 | tee "$S/f64seed1.log"
echo "=== f64seed 777001 x200000 (all4) ==="
"$EXE" f64seed 777001 200000 2>&1 | tee "$S/f64seed2.log"
echo "=== f32seed 987654 x100000 (all4) ==="
"$EXE" f32seed 987654 100000 2>&1 | tee "$S/f32seed.log"
echo "DONE $(date '+%H:%M:%S')"
