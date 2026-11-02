#!/usr/bin/env bash
# f32shard.sh - one sampled f32 shard (2^24 contiguous patterns) x log pair.
# Usage: f32shard.sh SHARD   (0..255); range [SHARD*2^24,(SHARD+1)*2^24).
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
ulimit -v 4194304
cd "$SCR" || exit 9
S=${1:?shard index}
LO=$(printf '%x' $((S * 16777216)))
HI=$(printf '%x' $(((S + 1) * 16777216)))
for fn in log2 log2p1; do
  ./build/vlog2.exe sweep f32 "$fn" "$LO" "$HI" > "logs/shard${S}_${fn}.log" 2>&1
  echo "shard $S $fn rc=$? :: $(tail -1 logs/shard${S}_${fn}.log)"
done
