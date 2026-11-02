#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "Wave 0 pushed: 2bac8e9 READY-verified, detailed body, remote confirms" < scratch/lead/wave0-pushed.txt
echo rc=$?
tail -8 ledger/lead.md
