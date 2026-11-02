#!/bin/sh
cd /mnt/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6ci/dup || exit 9
export MSF_PYTHON=python3
python3 --version
bash tools/run.sh smoke 2>&1 | tail -40
