#!/usr/bin/env bash
# verifier-w164 (5): implemented.tsv + off-limits claims analysis.
set -uo pipefail
G=/c/Program\ Files/Git/bin/git.exe
V=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
M=/c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat
echo "=== data rows (non-#, non-empty) base/copy/main ==="
for r in "4cdb912:$V" "WORKTREE:$V" "MAIN:$M"; do :; done
"$G" -c safe.directory="$V" -C "$V" show 4cdb912:tables/implemented.tsv | grep -v '^#' | grep -c .
echo "copy: $(grep -v '^#' "$V/tables/implemented.tsv" | grep -c .)"
echo "main: $(grep -v '^#' "$M/tables/implemented.tsv" | grep -c .)"
echo "=== copy wave-1 msf64 rows ==="
grep -c $'^msf64_.*\t1$' "$V/tables/implemented.tsv" || true
echo "=== new names in copy vs base (should be 173, all msf64_ wave 1) ==="
"$G" -c safe.directory="$V" -C "$V" show 4cdb912:tables/implemented.tsv | grep -v '^#' | grep . | sort > /tmp/impl-base.txt
grep -v '^#' "$V/tables/implemented.tsv" | grep . | sort > /tmp/impl-copy.txt
comm -13 /tmp/impl-base.txt /tmp/impl-copy.txt > /tmp/impl-new.txt
wc -l < /tmp/impl-new.txt
grep -vc $'^msf64_.*\t1$' /tmp/impl-new.txt || true
echo "=== removed names base->copy (should be 0) ==="
comm -23 /tmp/impl-base.txt /tmp/impl-copy.txt | wc -l
echo "=== copy data rows vs main data rows ==="
grep -v '^#' "$M/tables/implemented.tsv" | grep . | sort > /tmp/impl-main.txt
diff /tmp/impl-copy.txt /tmp/impl-main.txt | head -n 10
echo "diff-rc=$?"
