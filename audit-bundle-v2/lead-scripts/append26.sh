#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "RULING: parcel-f32 escalation upheld - pack tininess is delivered-value, Clause 7.5/Berkeley is unbounded-rounded; lead fixes kernel+reference+ingest" < scratch/lead/tininess-ruling.txt
echo rc=$?
rm -f ledger/urgent/parcel-f32-tininess-kernel.md
echo urgent cleared
