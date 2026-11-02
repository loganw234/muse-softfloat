#!/usr/bin/env bash
# 90_ekregen.sh - LEG Ek: rerun table generator in scratch, byte-compare.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
OUT="$D/ekregen"
mkdir -p "$OUT"
echo "python: $(python3 --version 2>&1) mpmath $(python3 -c 'import mpmath; print(mpmath.__version__)')"
echo "copy HEAD: $(git -C "$COPY" rev-parse HEAD)"
START=$(date +%s)
python3 "$COPY/tools/gen_explog_tables.py" "$OUT/msf_explog_tables.h" 2>&1 | tee "$OUT/gen.log"
echo "wall $(( $(date +%s) - START ))s"
echo "--- byte compare ---"
if cmp -s "$COPY/src/msf_explog_tables.h" "$OUT/msf_explog_tables.h"; then
  echo "EK REGEN: byte-identical"
else
  echo "EK REGEN: DIFFERS"
  diff "$COPY/src/msf_explog_tables.h" "$OUT/msf_explog_tables.h" | head -20
fi
echo "--- claimed integers check ---"
grep -m1 "EK_EXP" "$OUT/msf_explog_tables.h"
grep -m1 "NTERMS\|TERM" "$OUT/msf_explog_tables.h" | head -3
grep -o "MSF_EXPLOG_EK_EXP[^;]*" "$COPY/src/msf_explog_tables.h" | head -3
echo "--- gen_tables drift (4 files) ---"
mkdir -p "$OUT/gen-check"
python3 "$COPY/tools/gen_tables.py" "$OUT/gen-check" > "$OUT/gen_tables.log" 2>&1 || { echo "gen_tables FAILED"; tail -5 "$OUT/gen_tables.log"; }
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  if cmp -s "$COPY/$f" "$OUT/gen-check/$f"; then echo "drift $f: identical";
  else echo "drift $f: DIFFERS"; fi
done
