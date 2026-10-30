#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger verifier-approval "READY on 0bfa964 SF-0 approval + MIT licence recording (lead-filed staged body; child sandbox had no bash)" < scratch/lead/verifier-approval-body.txt
echo rc=$?
tail -8 ledger/verifier-approval.md
