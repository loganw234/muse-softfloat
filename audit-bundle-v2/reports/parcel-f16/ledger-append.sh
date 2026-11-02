#!/usr/bin/env bash
# usage: ledger-append.sh <headline> <bodyfile>
set -euo pipefail
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f16/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-f16\tmp'
export TEMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-f16\tmp'
mkdir -p "$TMPDIR"
cd /c/Users/logan/source/repos/Muse-Softfloat
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger parcel-f16 "$1" < "$2"
