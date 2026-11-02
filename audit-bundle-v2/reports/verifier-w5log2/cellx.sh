#!/usr/bin/env bash
# cellx.sh - investigate f64 log2 0x0170000000000000 in both drivers.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
ulimit -v 4194304
cd "$SCR" || exit 9
./build/vlog2.exe one f64 log2 0170000000000000 2>&1 | head -8
echo "=== parcel harness:"
./build/own_exhaustive.exe one 2 2 0170000000000000 2>&1 | head -8
