#!/usr/bin/env bash
# s13_seam_claims.sh - seam census, format parity, claim surface vs
# parent 0f08aa3, VECTORS tag rows.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR="$(pwd)/scratch/verifier-w5alg2/tmp"
export TMP="$TMPDIR" TEMP="$TMPDIR"
mkdir -p "$TMPDIR" scratch/verifier-w5alg2/out
ulimit -v 1048576
OUT=scratch/verifier-w5alg2/out
COPY=worktrees/verify5-alg2
{
echo "--- implemented.tsv hypot/r_sqrt rows ---"
grep -E "hypot|r_sqrt" $COPY/tables/implemented.tsv
echo "--- COVERAGE hypot rows (status col) ---"
grep "hypot" $COPY/docs/COVERAGE.tsv | cut -f1,9
echo "--- dispatch hypot (NULL = planned) ---"
grep -n "msf32_hypot\|msf16_hypot\|msf64_hypot" $COPY/tests/msf_dispatch.h | grep -c "NULL" || true
grep -n "hypot" $COPY/tests/msf_dispatch.h | head -8
echo "--- VECTORS.md tag rows ---"
grep -n "mpfr-alg" $COPY/tests/VECTORS.md
echo "--- git state of copy ---"
git -C $COPY status --short | head -5
git -C $COPY log --format="%H %s" -3
echo "--- claim surface vs parent 0f08aa3 ---"
git -C $COPY diff 0f08aa39c94d5682711138956b7a8a4c3e898e0b --stat
} 2>&1 | tee $OUT/s13_seam_claims.log
