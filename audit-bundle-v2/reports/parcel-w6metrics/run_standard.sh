#!/usr/bin/env bash
WS=/c/Users/logan/source/repos/Muse-Softfloat
export MSF_PYTHON=$WS/.venv/Scripts/python.exe
export TMPDIR=$WS/scratch/parcel-w6metrics/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w6metrics\tmp'
export TEMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w6metrics\tmp'
mkdir -p "$TMPDIR"
cd "$WS/worktrees/w6-metrics" || exit 1
time bash tools/run.sh standard
echo "exit=$?"
