#!/bin/bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 1
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-sf0/tmp
mkdir -p "$TMPDIR"
export TMP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-sf0/tmp"
export TEMP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-sf0/tmp"
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger verifier-sf0 "verifier-sf0 on 33c59f9: NOT READY, (a) 0 (b) 6" < scratch/verifier-sf0/ledger-body.txt
echo "ledger exit: $?"
tail -12 ledger/verifier-sf0.md
