#!/usr/bin/env bash
set -eu
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-f32/tmp
mkdir -p "$TMPDIR"
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger parcel-f32 "Design entry: 173 counted, special-value tables and kernel instances before code" < scratch/parcel-f32/design-body.txt
