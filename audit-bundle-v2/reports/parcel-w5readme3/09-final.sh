#!/usr/bin/env bash
# 09-final.sh - final verification: gate, links, stale sweeps, ownership, LF.
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS" || exit 9
ulimit -t 1800 2>/dev/null || true
export MSF_PYTHON=$WS/.venv/Scripts/python.exe
export TMPDIR=$WS/scratch/parcel-w5readme3/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
WT=$WS/worktrees/w5-readme3
OUT=$WS/scratch/parcel-w5readme3/out
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
rc_all=0

echo "--- smoke gate on the edited tree ---"
cd "$WT" || exit 9
bash tools/run.sh smoke > "$OUT/smoke-final.log" 2>&1
rc=$?
echo "smoke exit: $rc"
grep -E '^(total|VERDICT|inventory|budget)' build/smoke/verify.log
tail -2 "$OUT/smoke-final.log"
[ $rc -ne 0 ] && rc_all=1

echo "--- link check ---"
"$MSF_PYTHON" "$WS/scratch/parcel-w5readme3/linkcheck.py" > "$OUT/linkcheck.log" 2>&1
rc=$?
cat "$OUT/linkcheck.log"
[ $rc -ne 0 ] && rc_all=1

echo "--- stale-number sweep (expect no hits in hand-written texts) ---"
grep -nE '822 of 822|171,423|61 of 65|255|39 Tier|under way|authorised prefix' README.md && rc_all=1 || echo "README.md: clean"
grep -nE '810 of|1,596|in progress|authorised prefix|1\.58' site/index.html site/app.js site/README.md && rc_all=1 || echo "site texts: clean"
echo "--- unmodified sweep (expect REBOUND-desktop + KissFFT disclaimer only) ---"
grep -ni 'unmodified' README.md site/index.html site/README.md site/app.js || true
echo "--- CRLF check on hand-edited files ---"
"$MSF_PYTHON" -c "
from pathlib import Path
wt = Path('$WT')
bad = []
for f in ['README.md','site/build_data.py','site/build.py','site/glue.c','site/app.js','site/index.html','site/README.md','docs/metrics/briefs.jsonl']:
    b = (wt/f).read_bytes()
    if b'\r\n' in b: bad.append(f)
print('CRLF files:', bad if bad else 'none')
raise SystemExit(1 if bad else 0)
" || rc_all=1

echo "--- ownership: git status (expect README.md, site/**, briefs.jsonl only) ---"
git -c "safe.directory=$WT" -C "$WT" status --short
echo "--- diff stat ---"
git -c "safe.directory=$WT" -C "$WT" diff --stat | tail -16
echo "FINAL-CHECKS exit: $rc_all"
exit $rc_all
