#!/usr/bin/env bash
# 92_driftdiff.sh - show what differs in gen_tables regen.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
OUT="$D/ekregen"
{
echo "=== muse_softfloat.h ==="
diff "$COPY/include/muse_softfloat.h" "$OUT/gen-check/include/muse_softfloat.h" | head -20
echo "=== msf_dispatch.h (first 20) ==="
diff "$COPY/tests/msf_dispatch.h" "$OUT/gen-check/tests/msf_dispatch.h" | head -20
echo "=== COVERAGE.tsv (first 20) ==="
diff "$COPY/docs/COVERAGE.tsv" "$OUT/gen-check/docs/COVERAGE.tsv" | head -20
echo "=== counts ==="
diff "$COPY/include/muse_softfloat.h" "$OUT/gen-check/include/muse_softfloat.h" | wc -l
diff "$COPY/tests/msf_dispatch.h" "$OUT/gen-check/tests/msf_dispatch.h" | wc -l
diff "$COPY/docs/COVERAGE.tsv" "$OUT/gen-check/docs/COVERAGE.tsv" | wc -l
} 2>&1 | tee "$D/92_driftdiff.log"
