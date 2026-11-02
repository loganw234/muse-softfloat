#!/usr/bin/env bash
# f32shards.sh - run sampled shards 0,1,128,255 in parallel (4 workers).
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
cd "$SCR" || exit 9
for s in 0 1 128 255; do
  ./f32shard.sh "$s" > "logs/shards${s}.log" 2>&1 &
done
wait
echo "all shards done"
grep -H . logs/shards*.log
