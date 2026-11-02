#!/usr/bin/env bash
# One op of the one-time exhaustive binary16 pairs run:
# 256 shards x (256 first operands x 65536 second) = 2^32.
set -u
source "$(dirname "$0")/env.sh"
OP="${1:?op}"
EXE="$WS/scratch/parcel-w5aug/tmp/exh/aug_exhaustive.exe"
DIR="$WS/scratch/parcel-w5aug/logs/exh-$OP"
mkdir -p "$DIR"
ulimit -v 262144
echo "op=$OP ulimit-v=$(ulimit -v) (KB) exe=$EXE"
echo "priority: harness sets BELOW_NORMAL_PRIORITY_CLASS itself"
start=$(date +%s)
done_count=0
for lo in $(seq 0 256 65280); do
  hi=$((lo + 256))
  log="$DIR/shard-$lo.log"
  if [ -f "$log" ] && grep -q 'VERDICT: PASS' "$log"; then
    echo "skip done shard $OP $lo"
  else
    "$EXE" pairs "$OP" "$lo" "$hi" > "$log" 2>&1
    rc=$?
    if [ $rc -ne 0 ] || ! grep -q 'VERDICT: PASS' "$log"; then
      echo "SHARD FAILED $OP $lo rc=$rc"
      cat "$log"
      exit 1
    fi
  fi
  done_count=$((done_count + 1))
  if [ $((done_count % 32)) -eq 0 ]; then
    echo "progress $OP $done_count/256 elapsed=$(( $(date +%s) - start ))s $(date '+%H:%M:%S')"
  fi
done
echo "all shards done $OP elapsed=$(( $(date +%s) - start ))s"
"$MSF_PYTHON" "$WS/scratch/parcel-w5aug/scripts/exhaustive_aggregate.py" "$OP"
