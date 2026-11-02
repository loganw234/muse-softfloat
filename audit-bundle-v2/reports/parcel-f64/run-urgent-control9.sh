#!/usr/bin/env bash
set -euo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-f64/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-f64\tmp'
export TEMP="$TMP"
bash softfloat-bootstrap-kit/tools/ledger.sh urgent ledger parcel-f64 control9 "smoke control planned-only uses msf64_add, now implemented here" < scratch/parcel-f64/urgent-control9-body.txt
cat ledger/urgent/parcel-f64-control9.md
