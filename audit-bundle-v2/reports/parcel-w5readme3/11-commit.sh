#!/usr/bin/env bash
# 11-commit.sh - two detailed commits, owned files only. Never push/merge.
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS" || exit 9
WT=$WS/worktrees/w5-readme3
G() { git -c "safe.directory=$WT" -C "$WT" "$@"; }
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "branch: $(G branch --show-current) HEAD: $(G rev-parse --short HEAD)"
G add site/README.md site/app.js site/build.py site/build_data.py site/data.json site/glue.c site/index.html site/msf.wasm site/ops.json site/replay-log.txt site/vectors-sample.json || exit 1
echo "--- staged for commit 1 ---"
G diff --cached --name-only
G commit -F "$WS/scratch/parcel-w5readme3/commit1.txt" || exit 1
G add README.md docs/metrics/briefs.jsonl || exit 1
echo "--- staged for commit 2 ---"
G diff --cached --name-only
G commit -F "$WS/scratch/parcel-w5readme3/commit2.txt" || exit 1
echo "--- log ---"
G --no-pager log --oneline -4
echo "--- status (expect clean; build/ is gitignored) ---"
G status --short
echo "COMMITS DONE"
