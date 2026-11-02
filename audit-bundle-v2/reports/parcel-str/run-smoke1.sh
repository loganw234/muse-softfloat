#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
export TMPDIR=$ROOT/scratch/parcel-str/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR"
cd "$W" || exit 9
bash tools/run.sh smoke > "$ROOT/scratch/parcel-str/smoke1.log" 2>&1
echo "smoke rc=$?"
cat "$ROOT/scratch/parcel-str/smoke1.log"
