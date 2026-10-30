#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "SF-0 drafting started; expanded IEEE 754 scope as gated tiers" < scratch/lead/sf0-start.txt
echo rc=$?
