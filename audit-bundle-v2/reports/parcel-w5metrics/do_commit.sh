#!/usr/bin/env bash
# Commit the metrics appends on wave5-metrics. Never push/merge.
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-metrics" || exit 1
git status --short
git add docs/metrics/usage.jsonl docs/metrics/passes.jsonl docs/metrics/escalations.jsonl docs/metrics/briefs.jsonl
git diff --cached --stat
git commit -F "$WS/scratch/parcel-w5metrics/commit_msg.txt" || exit 1
git log --oneline -3
git status --short
git show -s --format="%H %cI" HEAD
