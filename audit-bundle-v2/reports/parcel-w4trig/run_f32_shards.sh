#!/usr/bin/env bash
# Binary32 exhaustive finite differential: 32 magnitude
# shards of 2^26 (both signs each), up to 8 concurrent.
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
O=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out/f32shards
mkdir -p "$O"
SHARD=67108864
MAXJ=8
START=$(date +%s)
echo "f32 exhaustive launch $(date) shard_size=$SHARD max_jobs=$MAXJ"
run_shard() {
  local i=$1 lo hi
  lo=$(( i * SHARD ))
  hi=$(( lo + SHARD ))
  local s=$(date +%s)
  build/trig/trig_exhaustive.exe f32 "$lo" "$hi" > "$O/shard_$(printf %02d $i).log" 2>&1
  echo "shard $i rc=$? in $(( $(date +%s) - s ))s" >> "$O/progress.log"
}
: > "$O/progress.log"
for i in $(seq 0 31); do
  while [ "$(jobs -r | wc -l)" -ge "$MAXJ" ]; do wait -n; done
  run_shard "$i" &
done
wait
echo "all shards done in $(( $(date +%s) - START ))s"
cat "$O/progress.log"
grep -h '^f32 shard:' "$O"/shard_*.log
grep -h '^counters:' "$O"/shard_*.log
