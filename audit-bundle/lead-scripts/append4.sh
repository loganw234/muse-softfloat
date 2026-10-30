#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "Owner word: Co-Authored-By trailer naming the model on every AI commit" < scratch/lead/coauthor.txt
echo rc=$?
