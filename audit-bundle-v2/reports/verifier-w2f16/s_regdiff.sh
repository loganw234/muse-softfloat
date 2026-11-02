#!/usr/bin/env bash
# s_regdiff.sh - show regen vs committed diffs
set -u
CP="C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16"
SC="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
cd "$CP" || exit 9
echo "=== arith-f16.vec regen-diff ==="
diff "$SC/regen/arith-f16.vec" tests/vectors/arith-f16.vec | head -30
echo "=== arith diff line count ==="
diff "$SC/regen/arith-f16.vec" tests/vectors/arith-f16.vec | grep -c '^[<>]'
echo "=== conv-int-f16.vec regen-diff ==="
diff "$SC/regen/conv-int-f16.vec" tests/vectors/conv-int-f16.vec | head -30
echo "=== conv-int diff line count ==="
diff "$SC/regen/conv-int-f16.vec" tests/vectors/conv-int-f16.vec | grep -c '^[<>]'
