#!/usr/bin/env bash
# regen1.sh - gen_tables.py re-run into scratch; diff vs committed.
set -u
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
cd "$COPY" || exit 9
rm -rf "$SCR/gentab1"
"$PY" tools/gen_tables.py "$SCR/gentab1" > "$SCR/logs/gentab1.log" 2>&1
echo "exit=$?"
tail -5 "$SCR/logs/gentab1.log"
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  if cmp -s "$f" "$SCR/gentab1/$f"; then echo "SAME $f"; else echo "DIFF $f"; fi
done
