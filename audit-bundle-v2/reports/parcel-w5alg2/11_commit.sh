#!/usr/bin/env bash
# 11_commit.sh - two detailed commits on wave5-alg2. Never push/merge.
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg2" || exit 9
S="$WS/scratch/parcel-w5alg2"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg2\tmp'
export TEMP="$TMP"
git branch --show-current
git status --porcelain

git add src/msf_alg.c tables/implemented.tsv include/muse_softfloat.h \
  docs/COVERAGE.tsv tests/msf_dispatch.h docs/WIDTHS.md tools/run.sh
git commit -F "$S/commit1.txt" > "$S/out/commit1.log" 2>&1; echo "commit1 rc=$?"
cat "$S/out/commit1.log"

git add tests/alg_decider.c tests/gen_vectors_alg.py \
  tests/vectors/alg-f16.vec tests/vectors/alg-f32.vec tests/vectors/alg-f64.vec \
  docs/metrics/briefs.jsonl
git commit -F "$S/commit2.txt" > "$S/out/commit2.log" 2>&1; echo "commit2 rc=$?"
cat "$S/out/commit2.log"

git log --oneline -4
git status --porcelain
echo "tree state above (empty status = clean)"
