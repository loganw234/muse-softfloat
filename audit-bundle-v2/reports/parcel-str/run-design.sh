#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$ROOT/scratch/parcel-str/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR"
bash "$ROOT/softfloat-bootstrap-kit/tools/ledger.sh" append "$ROOT/ledger" parcel-str "DESIGN ENTRY: grammar, exact algorithms, spec freeze, proposed vector format; 6 ruling bundles" < "$ROOT/scratch/parcel-str/design-body.txt"
echo "append rc=$?"
bash "$ROOT/softfloat-bootstrap-kit/tools/ledger.sh" urgent "$ROOT/ledger" parcel-str rulings "parcel-str: 6 ruling bundles with recommendations (design entry filed)" < "$ROOT/scratch/parcel-str/rulings-body.txt"
echo "urgent rc=$?"
head -3 "$ROOT/ledger/parcel-str.md"
