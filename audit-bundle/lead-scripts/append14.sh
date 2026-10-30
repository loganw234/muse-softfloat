#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "SF-0 pushed: 828b8f1 READY at study cap, awaiting Logan approval" < scratch/lead/sf0-pushed.txt
echo rc=$?
