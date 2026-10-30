#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "SF-0 approval + MIT licence verified and pushed (0bfa964); P0 gate open" < scratch/lead/approval-pushed.txt
echo rc=$?
tail -6 ledger/lead.md
