#!/usr/bin/env bash
# f32time.sh - time a 2^20 slice to price shards.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
ulimit -v 4194304
cd "$SCR" || exit 9
start=$(date +%s)
./build/vlog2.exe sweep f32 log2 0 100000 > logs/f32time.log 2>&1
echo "rc=$?"
tail -2 logs/f32time.log
end=$(date +%s)
echo "elapsed=$((end-start))s for 2^20 patterns x1fn x5modes"
