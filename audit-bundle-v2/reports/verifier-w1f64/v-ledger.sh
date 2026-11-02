#!/usr/bin/env bash
# verifier-w164: append ledger entry via kit ledger.sh.
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
LEDGER=$PWD/ledger
KIT=softfloat-bootstrap-kit/tools/ledger.sh
BODY=scratch/verifier-w1f64/ledger-body.txt
bash "$KIT" append "$LEDGER" verifier-w1f64 \
  "wave-1 binary64 parcel verdict: NOT READY (3 regressions, 3 wrong data)" < "$BODY"
echo "ledger rc=$?"
