#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "Rulings on parcel-f32 design entry: both wording faults and assumptions A1/A2 confirmed" < scratch/lead/f32-design-ruling.txt
echo rc=$?
