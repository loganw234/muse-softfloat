#!/bin/bash
# Probe 6: tools/run.sh standard in the duplicate (never the copy).
# Memory ceiling per parcel discipline; TMP inside verifier scratch.
set -u
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
export TMPDIR="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/tmp"
export TMP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/tmp"
export TEMP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/tmp"
mkdir -p "$TMPDIR"
ulimit -v 4194304
cd "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/dup"
bash tools/run.sh standard 2>&1 | tail -25
echo "STANDARD_RC=${PIPESTATUS[0]}"
