#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "rechecker-phase0 NOT READY: one new (b) was the lead's own clause; dropped" < scratch/lead/recheck2-disposition.txt
echo rc=$?
tail -8 ledger/lead.md
