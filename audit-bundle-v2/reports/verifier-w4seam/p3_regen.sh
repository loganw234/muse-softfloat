#!/usr/bin/env bash
# p3_regen.sh - regenerate to temp outdir, byte-compare all four files.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-seam
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4seam
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
cd "$COPY" || exit 9
rm -rf "$SCR/regen"
"$MSF_PYTHON" tools/gen_tables.py "$SCR/regen" > "$SCR/regen.log" 2>&1
echo "generator exit: $?"
cat "$SCR/regen.log"
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  if cmp -s "$f" "$SCR/regen/$f"; then echo "IDENTICAL: $f"; else echo "DIFFERS: $f"; fi
done
