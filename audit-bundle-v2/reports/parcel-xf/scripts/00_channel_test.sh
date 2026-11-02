#!/usr/bin/env bash
set -euo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/parcel-xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-xf\tmp'
export TEMP="$TMP"
mkdir -p "$TMPDIR"
printf 'For: lead\nChannel test from parcel-xf at start; no action needed beyond noting receipt.\n' \
  | bash "$ROOT/softfloat-bootstrap-kit/tools/ledger.sh" urgent "$ROOT/ledger" parcel-xf test "parcel-xf channel test"
ls -l "$ROOT/ledger/urgent/parcel-xf-test.md"
cat "$ROOT/ledger/urgent/parcel-xf-test.md"
