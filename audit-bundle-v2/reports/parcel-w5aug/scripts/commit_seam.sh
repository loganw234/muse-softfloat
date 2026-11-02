#!/usr/bin/env bash
set -eu
source "$(dirname "$0")/env.sh"
cat > "$WS/scratch/parcel-w5aug/tmp/commit-seam.txt" <<'EOF'
SF-2 Step 4 seam: aug_pair signature for Clause 9.5

Register augmented_add/sub/mul at binary16/32/64 (9 rows,
9.5, tier 2, C-754, project-exact, flags yes, rounding
fixed per pin P4; caller attribute forbidden). Tier 2 goes
to 66 registered / 57 implemented, 849 instantiations; the
augmented rows are planned in this commit.

Generator: aug_pair expands to struct-return pair
declarations; pair structs and the msf64_pair_t
hidden-pointer ABI note (16 B under the ARM AAPCS softfloat
convention; 4/8 B pairs return in registers) join the
header prelude, which also states that pair inexact tracks
pair exactness. rounding=fixed is validated and reserved
to aug_pair. Dispatch gains a pair_call field with
msf_pair_* two-result trampolines (single-result call
stays 0 for pair rows).

Runner: two-result lines (op - a b -> head tail flags
prov), both results exact-compared, two-result canonical
hash line. Board: harness replies R <head> <tail> <flags>
and folds the identical canonical line; host_replay
checks both pair results. run.sh names TIER2=66.

Gates this commit: regen twice byte-stable; smoke PASS
with the nine rows named planned. No kernel yet.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
EOF
git add tables/operations.tsv tools/gen_tables.py tools/run.sh \
  include/muse_softfloat.h tests/msf_dispatch.h docs/COVERAGE.tsv \
  tests/runner.c tests/VECTORS.md board/harness_main.c board/host_replay.py
git status --short
git commit -F "$WS/scratch/parcel-w5aug/tmp/commit-seam.txt"
git log --oneline -2
