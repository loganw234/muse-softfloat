#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "P0 host seam green (smoke 13s, standard 54s, 1.1M exhaustive vectors)" < scratch/lead/p0-host-seam.txt
echo rc=$?
