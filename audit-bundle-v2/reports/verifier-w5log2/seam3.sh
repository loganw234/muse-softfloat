#!/usr/bin/env bash
# seam3.sh - operations.tsv wave values for log rows.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
cd "$COPY" || exit 9
grep -n 'log2' tables/operations.tsv
echo "=== header of operations.tsv ==="
sed -n '1,12p' tables/operations.tsv
