#!/usr/bin/env bash
# p6_cross.sh - cross-checks: VECTORS cap vs runner.c; prelude wording;
# run.sh constants vs brief freeze; metrics row vs brief file.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-seam
WS=/c/Users/logan/source/repos/Muse-Softfloat
echo "--- runner.c MAX_PROV ---"; grep -n 'define MAX_PROV' "$COPY/tests/runner.c"
echo "--- VECTORS.md provenance paragraph ---"; grep -n -A5 'Provenance budget' "$COPY/tests/VECTORS.md"
echo "--- run.sh constants ---"; grep -n 'TOTAL_EXPECTED=' "$COPY/tools/run.sh"
echo "--- brief freeze (ledger/briefs/w4-seam.md) ---"; grep -n '783\|frozen at 33' "$WS/ledger/briefs/w4-seam.md" | head -8
echo "--- metrics row ---"; tail -1 "$COPY/docs/metrics/briefs.jsonl"
echo "--- header prelude tier2 paragraph ---"; grep -n -A4 'Tier 2 declarations' "$COPY/include/muse_softfloat.h"
echo "--- maximum table row ---"; awk -F'\t' '$1=="maximum"' "$COPY/tables/operations.tsv"
echo "--- maximum coverage rows ---"; awk -F'\t' '$2=="maximum" {print $1, $6, $7}' "$COPY/docs/COVERAGE.tsv"
