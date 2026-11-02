#!/usr/bin/env bash
# p2_claim.sh - claim surface vs copy parent (inside the copy only).
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-seam
cd "$COPY" || exit 9
echo "--- changed files ---"
git diff HEAD^ --name-only
echo "--- stat ---"
git diff HEAD^ --stat | tail -12
echo "--- src/msf_formats.h parent-vs-copy byte compare ---"
git show HEAD^:src/msf_formats.h | cmp - src/msf_formats.h && echo "msf_formats.h BYTE-IDENTICAL" || echo "msf_formats.h DIFFERS"
echo "--- forbidden-path check (expect no output) ---"
git diff HEAD^ --name-only | grep -E '^(src/|compat/|board/|tests/runner\.c|tables/implemented\.tsv|tests/vectors/|README\.md|docs/RECORD)' || echo "no forbidden-path changes"
echo "--- owned-list check ---"
git diff HEAD^ --name-only | grep -vE '^(tables/operations\.tsv|tools/gen_tables\.py|tools/run\.sh|include/muse_softfloat\.h|tests/msf_dispatch\.h|docs/COVERAGE\.tsv|src/msf_formats\.h|tests/VECTORS\.md|docs/metrics/briefs\.jsonl)$' || echo "all changed files in owned list"
