#!/usr/bin/env bash
# seam1.sh - read-only seam facts from the verify copy.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
cd "$COPY" || exit 9
echo "=== implemented.tsv header ==="
sed -n '1,20p' tables/implemented.tsv
echo "=== log2p1 rows ==="
grep -n 'log2p1' tables/implemented.tsv
echo "=== COVERAGE log2 rows ==="
grep -n 'log2' docs/COVERAGE.tsv | head -20
