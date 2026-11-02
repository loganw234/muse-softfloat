#!/usr/bin/env bash
# verifier-w4minmax s6: claim surface vs parent 8578114 + standard budget.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-minmax
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4minmax
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
OUT=$SCR/out-surface
mkdir -p "$OUT"
cd "$COPY" || exit 9
echo "== diff file list vs parent 8578114 =="
git diff --name-only 8578114 HEAD
echo "== diff stat vs parent =="
git diff --stat 8578114 HEAD | tail -18
echo "== lead-owned/forbidden touched? (formats, operations, decode, internal, roundpack, string, run.sh, README, RECORD, board) =="
git diff --name-only 8578114 HEAD | grep -E '^(tables/(formats|operations)\.tsv|src/(msf_decode\.h|msf_internal\.h|msf_roundpack\.c|msf_string\.c)|tools/run\.sh|README\.md|docs/RECORD\.md|board/)' && echo "TOUCHED-FORBIDDEN" || echo "untouched-ok"
echo "== implemented.tsv: 33 rows wave 4 =="
git diff 8578114 HEAD -- tables/implemented.tsv | grep -c '^+[^+]'
git diff 8578114 HEAD -- tables/implemented.tsv | grep '^+[^+]' | awk -F'\t' '{print $1, $NF}' | sort | uniq -c | head -8
echo "== operations.tsv rows for the 33 (sig/rounding/flags/tier/wave/claim) =="
grep -E 'minimum|maximum|payload' tables/operations.tsv | awk -F'\t' '{print $1, $2, $3, $4, $5, $6, $7}' | head -40
echo "== VECTORS.md new tag rows =="
git diff 8578114 HEAD -- tests/VECTORS.md
echo "== briefs.jsonl new row =="
git diff 8578114 HEAD -- docs/metrics/briefs.jsonl
echo "== COVERAGE tier2 claim tokens =="
awk -F'\t' '$13=="2" {print $9, $12}' docs/COVERAGE.tsv | sort | uniq -c
echo "== hand-written line ceiling (src + test code, excl generated+vectors) =="
git diff --numstat 8578114 HEAD -- src/msf_performat.inc include/muse_softfloat.h tests/gen_vectors_tier2.py tests/runner.c | awk '{a+=$1; d+=$2} END {print "added="a" deleted="d}'
echo "== header decls: minmax take flags, payloads take none =="
grep -cE 'msf(16|32|64)_(minimum|maximum)(.*flags' include/muse_softfloat.h
grep -E 'msf16_(minimum_number|get_payload|set_payload|set_payload_signaling)\(' include/muse_softfloat.h
echo "== standard budget =="
bash tools/run.sh standard > "$SCR/out-smoke/standard.log" 2>&1
echo "STANDARD_RC=$?"
tail -6 "$SCR/out-smoke/standard.log"
exit 0
