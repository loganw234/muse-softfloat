#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-filmretime || exit 9
mkdir -p /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6filmretime/tmp
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6filmretime/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w6filmretime\tmp'
export TEMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w6filmretime\tmp'
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
tools/run.sh standard > /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6filmretime/run_standard.log 2>&1
echo "rc=$?"
tail -n 30 /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6filmretime/run_standard.log
