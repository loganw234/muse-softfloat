#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
# staged body: drop its own first headline line if present, keep Measured/Believed/For
if head -1 scratch/rechecker2-sf0/ledger-body.txt | grep -q '^## '; then
  tail -n +3 scratch/rechecker2-sf0/ledger-body.txt > scratch/lead/rechecker2-body-nohead.txt
else
  cp scratch/rechecker2-sf0/ledger-body.txt scratch/lead/rechecker2-body-nohead.txt
fi
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger rechecker2-sf0 "rechecker2-sf0 on 828b8f1: READY, (a) 0 (b) 0 notes 1" < scratch/lead/rechecker2-body-nohead.txt
echo rc=$?
tail -8 ledger/rechecker2-sf0.md
