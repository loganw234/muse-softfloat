#!/usr/bin/env bash
set -u
source "$(dirname "$0")/env.sh"
"$MSF_PYTHON" "$WS/scratch/parcel-w5aug/scripts/test_host_replay.py" > "$WS/scratch/parcel-w5aug/logs/host-replay.log" 2>&1
rc=$?
echo "exit=$rc"
cat "$WS/scratch/parcel-w5aug/logs/host-replay.log"
exit $rc
