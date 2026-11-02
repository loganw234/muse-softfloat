#!/usr/bin/env bash
set -eu
source "$(dirname "$0")/env.sh"
cat > "$WS/scratch/parcel-w5aug/tmp/commit-evidence.txt" <<'EOF'
SF-2 Step 4 evidence: augmented vectors and f16 harness

tests/gen_vectors_aug.py is the project-exact authority:
an exact-Fraction reference for the ratified 9.5 table
(P1 = R2) with an independent neighbour-distance checker
re-deciding every emitted pair (generation refuses on
disagreement). Committed sets: aug-f16 46,088 + aug-f32
46,146 + aug-f64 46,146 = 138,380 lines (specials matrix
in both orders, RTTZ ties incl. binade crossings and the
algebraic mul-tie family, overflow-threshold tie and one
step each side with the mul tie by the 2^(p+1)-1
factorisation, verbatim huge-gap pairs, zero signs, P1
tiny-exact cells, mul below-step cells incl.
tail-zero-opposite-head, boundary pool cross product,
seeded sweeps). Regeneration is byte-identical (twice,
cmp against committed copies).

tests/aug_exhaustive.c carries a second, independent
binary16 reference in C: `pool` mode (every first operand
x a 28-value boundary pool x 3 ops = 5,505,024 cases) is
wired into `standard` as the standing leg; `pairs` mode
is the sharded shape for the one-time 2^32-per-name
recorded run. run.sh adds the three aug vector files to
every budget's manifest.

Watched refusing before this commit (parcel report):
all six MSF_AUG_TEST_* mutants fail the committed vectors
(te-head 5,478; zero-tail-sign 30,727; swap-pair 105,583;
jam-window 30,458; p1-opposite 14,558; pack-leak 39,626)
and a corrupted pair-tail expectation is refused.
smoke and standard PASS; ARM target-compile clean at
-Os and -O3; board harness firmware builds (no flash;
on-silicon replay is lead work under the lock).

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
EOF
git add tests/gen_vectors_aug.py tests/aug_exhaustive.c \
  tests/vectors/aug-f16.vec tests/vectors/aug-f32.vec \
  tests/vectors/aug-f64.vec tests/VECTORS.md tools/run.sh \
  docs/metrics/briefs.jsonl
git status --short
git commit -F "$WS/scratch/parcel-w5aug/tmp/commit-evidence.txt"
git log --oneline -4
git status --short
