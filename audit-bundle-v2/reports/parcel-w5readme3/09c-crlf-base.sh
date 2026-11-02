#!/usr/bin/env bash
# 09c-crlf-base.sh - are briefs.jsonl's CRLFs pre-existing at HEAD?
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS" || exit 9
WT=$WS/worktrees/w5-readme3
git -c "safe.directory=$WT" -C "$WT" show HEAD:docs/metrics/briefs.jsonl > scratch/parcel-w5readme3/out/briefs-at-head.jsonl
"$WS/.venv/Scripts/python.exe" scratch/parcel-w5readme3/crlf_base.py
