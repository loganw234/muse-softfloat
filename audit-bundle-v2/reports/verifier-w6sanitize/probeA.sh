#!/usr/bin/env bash
# Probe A: MSF_SANITIZE=full with a non-sanitize budget must REFUSE (exit 2).
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6sanitize/dup || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
MSF_SANITIZE=full bash tools/run.sh standard > ../probeA.log 2>&1
echo "rc=$?"
head -8 ../probeA.log
