#!/usr/bin/env bash
# 17b_claim.sh - show r_sqrt/hypot operations rows + CLAIM_BY_TIER gate.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
head -1 worktrees/verify5-alg1/tables/operations.tsv
grep -h "r_sqrt\|hypot" worktrees/verify5-alg1/tables/operations.tsv
echo "--- CLAIM_BY_TIER / AUTHORITIES in copy gen_tables.py ---"
grep -n "CLAIM_BY_TIER\s*=\|AUTHORITIES\s*=" worktrees/verify5-alg1/tools/gen_tables.py
sed -n "$(grep -n 'CLAIM_BY_TIER =' worktrees/verify5-alg1/tools/gen_tables.py | cut -d: -f1),+4p" worktrees/verify5-alg1/tools/gen_tables.py
echo "--- same gate at parent 7c3819c (main worktree tables absent? check) ---"
git -C worktrees/verify5-alg1 show 7c3819c:tables/operations.tsv | head -1
git -C worktrees/verify5-alg1 show 7c3819c:tables/operations.tsv | grep -c "2" || true
