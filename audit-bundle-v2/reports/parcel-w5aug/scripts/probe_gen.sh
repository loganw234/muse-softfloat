#!/usr/bin/env bash
set -u
source "$(dirname "$0")/env.sh"
"$MSF_PYTHON" "$WS/scratch/parcel-w5aug/scripts/probe_gen.py" "${1:-f16}" > "$WS/scratch/parcel-w5aug/logs/probe-gen-$1.log" 2>&1
rc=$?
echo "exit=$rc"
cat "$WS/scratch/parcel-w5aug/logs/probe-gen-$1.log"
exit $rc
