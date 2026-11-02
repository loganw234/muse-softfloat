#!/usr/bin/env bash
# probe5: claims - implemented rows, diff stat vs base, shared-file identity
set -u
W=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f32
S=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f32
cd "$W" || exit 9
{
echo "=== implemented.tsv wave-1 count ==="
awk -F'\t' '$2==1' tables/implemented.tsv | wc -l
echo "=== wave-1 rows not msf32_* ==="
awk -F'\t' '$2==1 && $1 !~ /^msf32_/ {print}' tables/implemented.tsv
echo "=== wave-0 rows ==="
awk -F'\t' '$2==0' tables/implemented.tsv | wc -l
echo "=== diff stat 4cdb912..HEAD ==="
git -c safe.directory="$W" diff --stat 4cdb912..HEAD
echo "=== diff names ==="
git -c safe.directory="$W" diff --name-only 4cdb912..HEAD
echo "=== shared-file identity vs base ==="
for f in src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf16.c src/msf64.c tests/runner.c tests/gen_vectors.py tools/gen_tables.py tools/run.sh; do
  if git -c safe.directory="$W" diff --quiet 4cdb912..HEAD -- "$f"; then echo "IDENTICAL $f"; else echo "CHANGED $f"; fi
done
} > "$S/p5-claims.log" 2>&1
echo done-probe5
