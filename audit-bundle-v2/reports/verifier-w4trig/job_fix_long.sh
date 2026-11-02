#!/bin/bash
# Job 2 (background): signfix full shards 0, 16, 31 + signfix f64seed.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
echo "job2 start: $(date -u +%FT%TZ)"
$V/tmp/trigx_fix.exe f32 0 67108864 > $V/out/f32sh0_fix.log 2>&1
echo "fix shard0 rc=$?"
tail -2 $V/out/f32sh0_fix.log
$V/tmp/trigx_fix.exe f32 1073741824 1140850688 > $V/out/f32sh16_fix.log 2>&1
echo "fix shard16 rc=$?"
tail -2 $V/out/f32sh16_fix.log
$V/tmp/trigx_fix.exe f32 2080374784 2147483648 > $V/out/f32sh31_fix.log 2>&1
echo "fix shard31 rc=$?"
tail -2 $V/out/f32sh31_fix.log
$V/tmp/trigx_fix.exe f64seed 777 1048576 > $V/out/f64seed_fix.log 2>&1
echo "fix f64seed rc=$?"
tail -2 $V/out/f64seed_fix.log
echo "job2 done: $(date -u +%FT%TZ)"
