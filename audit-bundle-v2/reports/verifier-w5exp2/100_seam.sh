#!/usr/bin/env bash
# 100_seam.sh - seam census from committed COVERAGE.tsv + claim surface.
set -u
D="$(dirname "$0")"
ROOT="$(cd "$D/../.." && pwd)"
COPY="$ROOT/worktrees/verify5-exp2"
{
echo "--- COVERAGE tier2 census (committed) ---"
python3 - "$COPY/docs/COVERAGE.tsv" <<'EOF'
import sys
t2i = t2p = t2 = 0
t1 = t1i = 0
bad = []
with open(sys.argv[1], encoding='utf-8') as fh:
    for ln in fh:
        if ln.startswith('#') or not ln.strip():
            continue
        c = ln.rstrip('\n').split('\t')
        if c[0] == 'name':
            continue
        tier, status, claim = c[12], c[8], c[13]
        if tier == '2':
            t2 += 1
            if status == 'implemented': t2i += 1
            elif status == 'planned': t2p += 1
            else: bad.append(c[0])
            if claim != 'C-754': bad.append(c[0] + ':claim')
        elif tier == '1':
            t1 += 1
            if status == 'implemented': t1i += 1
print("tier2 registered=%d implemented=%d planned=%d bad=%s" % (t2, t2i, t2p, bad))
print("tier1 total=%d implemented=%d" % (t1, t1i))
EOF
echo "--- exp2/log2 rows in implemented.tsv ---"
grep -c "planned" "$COPY/tables/implemented.tsv"
wc -l "$COPY/tables/implemented.tsv"
echo "--- VECS explog presence ---"
grep -o "explog-[a-z0-9]*\.vec" "$COPY/tools/run.sh" | sort -u
echo "--- TIER2_TOTAL_EXPECTED ---"
grep -n "TIER2_TOTAL_EXPECTED" "$COPY/tools/run.sh"
echo "--- claim surface: a0acf2a..HEAD stat ---"
git -C "$COPY" diff --stat a0acf2a HEAD | tail -25
} 2>&1 | tee "$D/100_seam.log"
