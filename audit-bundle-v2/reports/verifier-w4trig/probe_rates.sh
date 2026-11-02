#!/bin/bash
# Probe K: rate measurement for f64seed and f32-shard gates.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
time $V/tmp/trigx.exe f64seed 12345 2000 2>&1 | tail -2
echo "=== f32 rate probe: magnitudes [0, 2^20) ==="
time $V/tmp/trigx.exe f32 0 1048576 2>&1 | tail -3
