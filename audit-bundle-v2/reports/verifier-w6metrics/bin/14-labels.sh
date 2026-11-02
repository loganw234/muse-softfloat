#!/bin/bash
# Run probe-5c label scan with memory ceiling; labels only.
set -u
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
export DUP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/dup"
export OUT="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
ulimit -v 4194304
"$MSF_PYTHON" "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/bin/14-labels.py" 2>&1 | tee "$OUT/labels.log"
