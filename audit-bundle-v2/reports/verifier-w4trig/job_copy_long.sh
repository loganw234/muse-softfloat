#!/bin/bash
# Job 1 (background): copy f32 shard 31 [high] + copy f64seed 2^20.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
echo "job1 start: $(date -u +%FT%TZ)"
$V/tmp/trigx.exe f32 2080374784 2147483648 > $V/out/f32sh31_copy.log 2>&1
echo "copy shard31 rc=$?"
tail -2 $V/out/f32sh31_copy.log
$V/tmp/trigx.exe f64seed 777 1048576 > $V/out/f64seed_copy.log 2>&1
echo "copy f64seed rc=$?"
tail -2 $V/out/f64seed_copy.log
echo "job1 done: $(date -u +%FT%TZ)"
