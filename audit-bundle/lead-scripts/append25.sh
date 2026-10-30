#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "Confirmed parcel-f64 design entry readings; window invariant stated" < scratch/lead/f64-design-ruling.txt
echo rc=$?
