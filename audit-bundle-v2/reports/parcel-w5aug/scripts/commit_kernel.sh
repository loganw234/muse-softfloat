#!/usr/bin/env bash
set -eu
source "$(dirname "$0")/env.sh"
cp tools/run.sh "$WS/scratch/parcel-w5aug/tmp/run-full.sh"
"$MSF_PYTHON" "$WS/scratch/parcel-w5aug/scripts/split_runsh.py" "$REPO"
cat > "$WS/scratch/parcel-w5aug/tmp/commit-kernel.txt" <<'EOF'
SF-2 Step 4 kernel: Clause 9.5 augmented arithmetic

src/msf_aug.c implements augmented add/sub/mul at all three
formats behind the seam: add/sub form the exact sum in a
plain-shift 128-bit window when the operand bit span is at
most 127 and take the verbatim far-operand pair wider than
that; mul splits the exact 2p product at the head grid.
The head comes from the shared pack under the new internal
MSF_IROUND_RTTZ mode (value 5, pin P5, unreachable by any
caller attribute; round_inc increments strictly above the
midpoint and the mode joins overflow-to-infinity, so the
threshold tie delivers max-finite). The pack's scratch
flags are discarded unread: delivered flags are computed
from exact-residual tests per the ratified table
(overflow+inexact on head overflow, underflow+inexact in
mul's unrepresentable-residual cell, nothing else; pin P1
= R2, an exact tiny residual raises no flag, and head
tininess alone never leaks). Specials ride
msf_nan_delivery with the decided bits delivered twice.

docs/WIDTHS.md gains the augmented rows with the proof:
window bound, verbatim gap lemma including the
binade-crossing step below a power of two, the integer
p-bit rounding argument that the add/sub residual always
has at most p significant bits, the mul below-step
characterisation, and the residual-extraction shift
bounds. Six test-only MSF_AUG_TEST_* mutants are built in
for the evidence stage (ties-to-even head, exact-zero
tail sign flip, swapped pair, jam window, P1-opposite,
pack-flag leak), never defined in quoted builds.

Rows move to implemented: Tier 2 66/66, 849/849. Board
and host builds link src/msf_aug.c. Regen twice
byte-stable. Vectors and the exhaustive harness follow
in the evidence commit; this tree already passes smoke
with them staged locally (parcel report names the logs).

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
EOF
git add src/msf_aug.c src/msf_internal.h src/msf_roundpack.c \
  tables/implemented.tsv tools/run.sh include/muse_softfloat.h \
  tests/msf_dispatch.h docs/COVERAGE.tsv docs/WIDTHS.md \
  board/CMakeLists.txt board/run_board.sh
git status --short
git commit -F "$WS/scratch/parcel-w5aug/tmp/commit-kernel.txt"
cp "$WS/scratch/parcel-w5aug/tmp/run-full.sh" tools/run.sh
git log --oneline -3
git status --short
