#!/usr/bin/env bash
set -uo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/parcel-xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-xf\tmp'
export TEMP="$TMP"
cd "$ROOT/worktrees/w2-xf" || exit 9
bash tools/run.sh smoke > "$ROOT/scratch/parcel-xf/logs/11_smoke_full.log" 2>&1
echo "smoke exit=$?"
cat "$ROOT/scratch/parcel-xf/logs/11_smoke_full.log"
