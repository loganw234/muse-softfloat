#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "Extractor written; Wave 0 numbers measured to 11:31:34 cutoff" < scratch/lead/extractor-decision.txt
echo rc=$?
git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat -C muse-softfloat status --short
