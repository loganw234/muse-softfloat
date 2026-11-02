#!/usr/bin/env bash
# Probe 1: append-only proof. For each metrics file, the first N lines of
# HEAD (N = parent line count) must be byte-identical to the parent blob.
set -euo pipefail
ulimit -v 2097152 2>/dev/null || true
COPY="C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-metrics"
cd "C:/Users/logan/source/repos/Muse-Softfloat"
for f in usage passes escalations briefs; do
  parent_lines=$(git -C "$COPY" show HEAD~1:docs/metrics/$f.jsonl | wc -l)
  head_lines=$(git -C "$COPY" show HEAD:docs/metrics/$f.jsonl | head -n "$parent_lines" | wc -l)
  parent_sha=$(git -C "$COPY" show HEAD~1:docs/metrics/$f.jsonl | sha256sum | cut -d' ' -f1)
  head_sha=$(git -C "$COPY" show HEAD:docs/metrics/$f.jsonl | head -n "$parent_lines" | sha256sum | cut -d' ' -f1)
  total=$(git -C "$COPY" show HEAD:docs/metrics/$f.jsonl | wc -l)
  if [ "$parent_sha" = "$head_sha" ]; then status="IDENTICAL"; else status="MISMATCH"; fi
  echo "$f: parent_rows=$parent_lines head_rows=$total prefix=$status"
  echo "  parent_sha=$parent_sha"
  echo "  head_sha  =$head_sha"
done
echo "--- diff of appended region only (should show additions, no deletions of frozen rows) ---"
for f in usage passes escalations briefs; do
  n=$(git -C "$COPY" show HEAD~1:docs/metrics/$f.jsonl | wc -l)
  echo "== $f appended rows: $(( $(git -C "$COPY" show HEAD:docs/metrics/$f.jsonl | wc -l) - n ))"
done
git -C "$COPY" diff HEAD~1 HEAD --stat -- docs/metrics/
