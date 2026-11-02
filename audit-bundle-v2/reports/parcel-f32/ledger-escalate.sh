#!/usr/bin/env bash
set -eu
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-f32/tmp
mkdir -p "$TMPDIR"
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger parcel-f32 "ESCALATION: shared pack tininess definition vs Berkeley/Clause 7.5, plus ingest eq row" < scratch/parcel-f32/escalation-body.txt
printf 'Shared pack tininess definition contradicts Berkeley and Clause 7.5 at the smallest-normal boundary (102 mul/div cases, flags only); ingest eq maps to the wrong predicate (1967 cases). Ledger: ledger/parcel-f32.md escalation entry with counts and examples. Berkeley mul/div/eq counts are blocked on your ruling; I keep working other fronts.\nFor: lead\n' > scratch/parcel-f32/urgent-body.txt
bash softfloat-bootstrap-kit/tools/ledger.sh urgent ledger parcel-f32 tininess-kernel "Pack tininess vs Clause 7.5: rule needed (kernel + ingest eq)" < scratch/parcel-f32/urgent-body.txt
