#!/usr/bin/env bash
# 101_planned.sh - how are the 6 planned rows recorded in implemented.tsv?
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
{
grep -n "planned" "$COPY/tables/implemented.tsv"
echo "--- log2 rows ---"
grep -n "log2" "$COPY/tables/implemented.tsv"
echo "--- header ---"
head -3 "$COPY/tables/implemented.tsv"
echo "--- run.sh freeze comment ---"
sed -n '125,140p' "$COPY/tools/run.sh"
} 2>&1 | tee "$D/101_planned.log"
