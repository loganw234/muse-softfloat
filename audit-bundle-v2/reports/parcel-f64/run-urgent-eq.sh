#!/usr/bin/env bash
set -euo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-f64/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-f64\tmp'
export TEMP="$TMP"
bash softfloat-bootstrap-kit/tools/ledger.sh urgent ledger parcel-f64 ingest-eq "berkeley_ingest maps f64_eq to signaling; Berkeley eq is quiet (proof inside)" < scratch/parcel-f64/urgent-eq-body.txt
cat ledger/urgent/parcel-f64-ingest-eq.md
