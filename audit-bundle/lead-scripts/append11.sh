#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
tail -n +3 scratch/rechecker-sf0/ledger-body.txt > scratch/lead/rechecker-body-nohead.txt
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger rechecker-sf0 "rechecker-sf0 on 4f7f870: NOT READY, (a) 0 (b) 2" < scratch/lead/rechecker-body-nohead.txt
echo rc=$?
tail -8 ledger/rechecker-sf0.md
