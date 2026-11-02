#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
command -v git || { echo "git not on PATH"; exit 1; }
WS="$(cd .. && pwd)"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export TMPDIR="$WS/scratch/lead/tmp" TMP="$WS/scratch/lead/tmp" TEMP="$WS/scratch/lead/tmp"
mkdir -p "$TMPDIR"
[ -z "$(git status --porcelain)" ] || { echo "dirty tree - stop"; exit 1; }

cat > "$TMPDIR/mm.txt" <<'EOF'
Merged the web demo page: the real library in WebAssembly

Merges wave5-site (36f12c6 + cd09700). site/ is a fully
static, dependency-free demo for GitHub Pages: the repo's
own src/*.c compiled unmodified to WebAssembly (Zig cc,
scratch-fetched, hash-recorded), an instrument UI over
810 runnable instantiations with bit-field breakdown and
flag chips, a deal-a-committed-vector mode, workload and
verification sections whose numbers are generated from
COVERAGE/metrics (828 instantiations, 182,518 vectors,
plants 75 of 80), and a labelled degraded mode when WASM
is unavailable. Proven at build time: 1,596 bundled
committed vectors replay through the WASM build under
Node, 0 mismatches; .github/workflows/pages.yml uploads
site/ as the Pages artifact.

Planted-copy verification (verifier-w5site, Spark): NOT
READY on the planted copy as constructed, 5 of 5 caught
(80 of 85 cumulative), no non-plant defect; the degraded
mode was exercised in a real browser engine. Pages
enablement follows this merge.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
EOF
git merge --no-ff wave5-site -F "$TMPDIR/mm.txt" || exit 1

cat "$WS/scratch/lead/plants-w5site.jsonl" >> docs/metrics/plants.jsonl
"$MSF_PYTHON" - <<'PYEOF'
import json
n = sum(1 for l in open("docs/metrics/plants.jsonl", encoding="utf-8") if l.strip() and json.loads(l))
print("plants.jsonl OK", n, "rows")
PYEOF
[ $? -eq 0 ] || exit 1
cat > "$TMPDIR/pm.txt" <<'PEOF'
Landed verifier-w5site plant grades (5 of 5)

80 of 85 cumulative.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
PEOF
git add docs/metrics/plants.jsonl && git commit -F "$TMPDIR/pm.txt" || exit 1

echo "--- smoke on merge tree ---"
bash tools/run.sh smoke; rc=$?
echo "smoke rc=$rc"
git log --oneline -4
exit $rc
