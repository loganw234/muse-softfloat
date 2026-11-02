#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$ROOT/scratch/parcel-str/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR"
bash "$ROOT/softfloat-bootstrap-kit/tools/ledger.sh" urgent "$ROOT/ledger" parcel-str test "parcel-str escalation channel test (Wave 3 dispatch)" < "$ROOT/scratch/parcel-str/urgent-test-body.txt"
echo "rc=$?"
ls -la "$ROOT/ledger/urgent/" | grep parcel-str || true
cat "$ROOT/ledger/urgent/parcel-str-test.md" 2>/dev/null || true
