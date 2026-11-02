#!/usr/bin/env bash
# 93_confirms.sh - confirm EK determinism + operations.tsv flags field.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
OUT="$D/ekregen"
{
echo "--- operations.tsv header ---"
head -2 "$COPY/tables/operations.tsv"
echo "--- exp2/exp2m1 rows ---"
grep -F "exp2" "$COPY/tables/operations.tsv" | cut -f1-8
echo "--- EK second regen determinism ---"
python3 "$COPY/tools/gen_explog_tables.py" "$OUT/msf_explog_tables_h2.h" > /dev/null 2>&1
if cmp -s "$OUT/msf_explog_tables.h" "$OUT/msf_explog_tables_h2.h"; then
  echo "generator deterministic: regen1 == regen2"
else
  echo "generator NONDETERMINISTIC across runs"
fi
echo "--- committed header EK line ---"
grep -n "EK_EXP\[3\]" "$COPY/src/msf_explog_tables.h"
echo "--- regen EK line ---"
grep -n "EK_EXP\[3\]" "$OUT/msf_explog_tables.h"
} 2>&1 | tee "$D/93_confirms.log"
