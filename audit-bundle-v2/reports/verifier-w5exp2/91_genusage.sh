#!/usr/bin/env bash
# 91_genusage.sh - check generator CLI/paths.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
{
grep -n "sys.argv" "$COPY/tools/gen_tables.py" | head -5
grep -n "def main" "$COPY/tools/gen_tables.py" | head -5
sed -n '1,40p' "$COPY/tools/gen_tables.py"
} 2>&1 | tee "$D/91_genusage.log"
