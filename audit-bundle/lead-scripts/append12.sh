#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "SF-0 draft 3: rechecker 0,2 accounting faults restated; re-check 2 next" < scratch/lead/sf0-draft3.txt
echo rc=$?
