#!/usr/bin/env bash
set -euo pipefail
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f16/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-f16\tmp'
export TEMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-f16\tmp'
mkdir -p "$TMPDIR"
cd /c/Users/logan/source/repos/Muse-Softfloat
bash softfloat-bootstrap-kit/tools/ledger.sh urgent ledger parcel-f16 test "parcel-f16 channel test" < scratch/parcel-f16/urgent-test-body.txt
cat ledger/urgent/parcel-f16-test.md
