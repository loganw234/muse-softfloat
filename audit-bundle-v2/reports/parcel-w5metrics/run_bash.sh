#!/usr/bin/env bash
# Common runner: Git Bash, MSF_PYTHON pinned to workspace .venv, TMP in scratch.
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
export MSF_PYTHON=$WS/.venv/Scripts/python.exe
export TMPDIR=$WS/scratch/parcel-w5metrics/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5metrics\tmp'
export TEMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5metrics\tmp'
mkdir -p "$TMPDIR"
ulimit -v 8388608 2>/dev/null || true
echo "MSF_PYTHON=$MSF_PYTHON"
"$MSF_PYTHON" --version
exec "$@"
