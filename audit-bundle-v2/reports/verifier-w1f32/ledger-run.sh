#!/usr/bin/env bash
set -u
W=/c/Users/logan/source/repos/Muse-Softfloat
cd "$W" || exit 9
LEDGER="$W/ledger"
KIT="$W/softfloat-bootstrap-kit/tools/ledger.sh"
bash "$KIT" append "$LEDGER" verifier-w1f32 "wave-1 binary32 parcel verified NOT READY (div 2x, div0 flag, sub inf sign)" < scratch/verifier-w1f32/ledger-body.md
echo "LEDGER_EXIT=$?"
tail -n 5 "$LEDGER/verifier-w1f32.md"
