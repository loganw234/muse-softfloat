#!/usr/bin/env bash
# 70_f32shards.sh - LEG f32: stratified sampled shards + seeded volume.
# All sequential, memory ceiling set. Shard arithmetic recorded in logs.
set -u
D="$(dirname "$0")"
ulimit -v 4194304
V="$D/build/vdriver.exe"
START=$(date +%s)
run() { # name lo hi [fn]
  echo "== shard $1 [$2,$3) fn=${4:-both} =="
  "$V" f32 "$2" "$3" ${4:-2} 2>&1 | tail -3
}
{
run S1-subnormal 00000000 00040000
run S2-one 3F000000 3F040000
run S3-tie25 4BFC0000 4C040000
run S4-overflow 43000000 43040000
run S5-etie  C3140000 C3180000
run S6-sat25 C1C60000 C1CA0000
run S7-w0 10000000 10008000
run S7-w1 20000000 20008000
run S7-w2 30000000 30008000
run S7-w3 40000000 40008000
run S7-w4 50000000 50008000
run S7-w5 60000000 60008000
run S7-w6 70000000 70008000
run S7-w7 08000000 08008000
echo "== seeded f32 (2 seeds x 200k) =="
"$V" f32seed 11 200000 2>&1 | tail -2
"$V" f32seed 77 200000 2>&1 | tail -2
echo "== seeded f64 (2 seeds x 200k) =="
"$V" f64seed 11 200000 2>&1 | tail -2
"$V" f64seed 77 200000 2>&1 | tail -2
echo "wall $(( $(date +%s) - START ))s"
} 2>&1 | tee "$D/70_f32shards.log"
