#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "Owner approved SF-0 recommendations; MIT licence; holder Logan W." < scratch/lead/sf0-approval.txt
echo rc=$?
tail -10 ledger/lead.md
