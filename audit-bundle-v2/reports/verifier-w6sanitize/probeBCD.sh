#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6sanitize/dup || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
echo "=== B: MSF_SANITIZE=bogus + sanitize ==="
MSF_SANITIZE=bogus bash tools/run.sh sanitize > ../probeB.log 2>&1
echo "rc=$?"
cat ../probeB.log
echo "=== C: MSF_SANITIZE=trap + sanitize ==="
MSF_SANITIZE=trap bash tools/run.sh sanitize > ../probeC.log 2>&1
echo "rc=$?"
cat ../probeC.log
echo "=== D: MSF_SANITIZE=full + sanitize ==="
MSF_SANITIZE=full bash tools/run.sh sanitize > ../probeD.log 2>&1
echo "rc=$?"
cat ../probeD.log
