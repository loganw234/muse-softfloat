#!/usr/bin/env bash
set -euo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-f64/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-f64\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR"
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger parcel-f64 "Re-gate by regater-f64: lead fixes merged, all blocked cases green, READY at cb10ee2" < scratch/parcel-f64/regate-ledger-body.txt
tail -8 ledger/parcel-f64.md
date -Iseconds
