#!/usr/bin/env bash
set -euo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-f64/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-f64\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR"
bash softfloat-bootstrap-kit/tools/ledger.sh urgent ledger parcel-f64 test "Escalation channel test parcel-f64 start $(date -Iseconds)" < scratch/parcel-f64/urgent-test-body.txt
cat ledger/urgent/parcel-f64-test.md
