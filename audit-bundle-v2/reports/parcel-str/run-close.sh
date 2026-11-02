#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$ROOT/scratch/parcel-str/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
bash "$ROOT/softfloat-bootstrap-kit/tools/ledger.sh" append "$ROOT/ledger" parcel-str "READY 8712ec1: 12 string rows gated (9,149 committed + 2.57M scratch + MPFR 47,857); only gap is lead control-9 retirement" < "$ROOT/scratch/parcel-str/close-body.txt"
echo "close rc=$?"
grep -c '^## ' "$ROOT/ledger/parcel-str.md"
tail -4 "$ROOT/ledger/parcel-str.md" | cut -c1-120
