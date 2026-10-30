#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "P0 complete pending commit: oracle built+priced, board replay+hello PASS on silicon, bench skeleton, metrics closing extract" < scratch/lead/p0-board-oracle.txt
echo rc=$?
cd muse-softfloat || exit 9
git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat status --short | head -60
git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat diff --stat | tail -5
