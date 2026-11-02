#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger verifier-p0 "READY on P0 23a740f (a)0 (b)0 notes 4 (lead-filed staged body; child sandbox ledger tool unrunnable)" < scratch/verifier-p0/ledger-body.txt
echo rc=$?
tail -4 ledger/verifier-p0.md
