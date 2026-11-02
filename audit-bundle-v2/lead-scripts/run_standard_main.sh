#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
mkdir -p /c/Users/logan/source/repos/Muse-Softfloat/scratch/lead/tmp
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/lead/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\lead\tmp'
export TEMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\lead\tmp'
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
tools/run.sh standard > /c/Users/logan/source/repos/Muse-Softfloat/scratch/lead/run_standard_main.log 2>&1
echo "rc=$?"
tail -n 15 /c/Users/logan/source/repos/Muse-Softfloat/scratch/lead/run_standard_main.log
