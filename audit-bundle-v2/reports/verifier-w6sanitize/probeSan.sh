#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6sanitize/dup || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
unset MSF_SANITIZE
bash tools/run.sh sanitize > ../sanitize-default.log 2>&1
echo "rc=$?"
grep -E "sanitizer flavour|canary|sanitized committed|total|VERDICT|budget sanitize|PASS|FAIL|SKIP" ../sanitize-default.log
