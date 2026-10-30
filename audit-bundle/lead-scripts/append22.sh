#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "P0 verified READY and pushed (23a740f + 36ca82e); Wave 1 gate open" < scratch/lead/p0-pushed.txt
echo rc=$?
cd muse-softfloat || exit 9
git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat status --porcelain; echo CLEAN_ABOVE
ls ../ledger/board.lock 2>/dev/null && echo LOCK_PRESENT || echo lock free
