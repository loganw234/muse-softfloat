#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "SF-0 draft 2: verifier-sf0 0,6 restated; scoped re-check next" < scratch/lead/sf0-draft2.txt
echo rc=$?
