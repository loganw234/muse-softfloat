#!/usr/bin/env bash
set -eu
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-sanitize
S="-c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-sanitize"
git $S status --short
git $S add tools/run.sh .github/workflows/ci.yml AGENTS.md docs/metrics/briefs.jsonl \
    tests/sanitize_canary_clean.c tests/sanitize_canary_ub.c tests/sanitize_canary_ub_shift.c \
    tests/sanitize_canary_heap.c tests/sanitize_canary_heap_far.c
git $S diff --cached --check
git $S diff --cached --stat
git $S commit -F /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6sanitize/commit-msg.txt
git $S log -1 --format='TIP %H %s'
git $S status --short -b
