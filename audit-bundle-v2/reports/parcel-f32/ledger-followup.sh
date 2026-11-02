#!/usr/bin/env bash
set -eu
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-f32/tmp
mkdir -p "$TMPDIR"
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger parcel-f32 "Berkeley big batch: 27.26M cases, failures only the two escalated classes" < scratch/parcel-f32/followup-body.txt
