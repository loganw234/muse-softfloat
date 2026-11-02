#!/usr/bin/env bash
set -u
source "$(dirname "$0")/env.sh"
ulimit -v 262144
for spec in "add 15360 15616" "mul 15360 15616" "mul 0 256" "sub 31744 32000"; do
  set -- $spec
  start=$(date +%s)
  "$WS/scratch/parcel-w5aug/tmp/exh/aug_exhaustive.exe" pairs "$1" "$2" "$3" > "$WS/scratch/parcel-w5aug/logs/exh-probe-$1-$2.log" 2>&1
  echo "$spec rc=$? elapsed=$(( $(date +%s) - start ))s $(head -1 "$WS/scratch/parcel-w5aug/logs/exh-probe-$1-$2.log")"
done
