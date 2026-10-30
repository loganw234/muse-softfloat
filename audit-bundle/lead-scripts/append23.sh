#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
mkdir -p scratch/lead/tmp scratch/lead/keys
export TMPDIR=$PWD/scratch/lead/tmp
bash softfloat-bootstrap-kit/tools/ledger.sh append ledger lead "Wave 1 dispatched: two format parcels from 4cdb912 (briefs in ledger/briefs/)" < scratch/lead/w1_dispatch.txt
echo ledger_rc=$?
cd muse-softfloat || exit 9
git worktree add ../worktrees/w1-f64 -b w1-f64 4cdb912dbd5ebda4fa2bc29168883dc4527d4091
echo wt64_rc=$?
git worktree add ../worktrees/w1-f32 -b w1-f32 4cdb912dbd5ebda4fa2bc29168883dc4527d4091
echo wt32_rc=$?
git worktree list
