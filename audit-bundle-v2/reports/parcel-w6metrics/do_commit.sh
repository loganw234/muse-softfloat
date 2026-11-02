#!/usr/bin/env bash
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w6-metrics" || exit 1
git status --porcelain
git diff --stat
git add docs/metrics/usage.jsonl docs/metrics/passes.jsonl docs/metrics/briefs.jsonl docs/metrics/escalations.jsonl
git commit -F "$WS/scratch/parcel-w6metrics/commit_msg.txt" || exit 1
git log --oneline -2
git show --stat --format="%H" HEAD | head -12
git status --porcelain
