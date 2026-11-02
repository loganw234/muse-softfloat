#!/usr/bin/env bash
# 07b-probes.sh - surface probes only (07's probe path broke after cd).
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS" || exit 9
ulimit -t 600 2>/dev/null || true
export TMPDIR=$WS/scratch/parcel-w5readme3/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
node "$WS/scratch/parcel-w5readme3/probe_wasm.mjs" "$WS/worktrees/w5-readme3/site" > "$WS/scratch/parcel-w5readme3/out/probe-wasm.log" 2>&1
rc=$?
cat "$WS/scratch/parcel-w5readme3/out/probe-wasm.log"
echo "probes exit: $rc"
exit $rc
