#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "Owner word: standing push and merge permission; verifiers to muse-spark-1.3 if able" < scratch/lead/standing-permission.txt
echo rc=$?
tail -6 ledger/lead.md
