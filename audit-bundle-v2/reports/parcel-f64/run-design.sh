#!/usr/bin/env bash
set -euo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-f64/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-f64\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR"
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger parcel-f64 "Design entry: 173 binary64 instantiations, kernel instances and special tables" < scratch/parcel-f64/design-body.txt
tail -5 ledger/parcel-f64.md
date -Iseconds
