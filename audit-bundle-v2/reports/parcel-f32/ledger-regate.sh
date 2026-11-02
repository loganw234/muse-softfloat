#!/usr/bin/env bash
set -eu
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-f32/tmp
mkdir -p "$TMPDIR"
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger parcel-f32 "Re-gate READY: b37fb12 merged, 27.3M Berkeley green, head 26c76aa unpushed" < scratch/parcel-f32/regate-ledger-body.txt
