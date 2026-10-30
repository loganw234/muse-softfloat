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
Merged demo/: one-script reproduction of the workloads

Merges wave5-demo (094538a, 3d3bfc0, 3feebb9). A stranger
with a fresh clone runs bash demo/run_demo.sh host and
gets the three evidences: the pinned REBOUND and KissFFT
archives are fetched into a gitignored cache and verified
(archive + licence SHA-256 against docs/metrics/
fetches.jsonl) before extraction - no REBOUND or KissFFT
source is ever tracked, and fetch refuses if the cache
path would be. The IAS15 extract regenerates
code-identical to the silicon-proven one; the KissFFT
Fork B tree hash-matches the recorded board-run files;
host proofs check IAS15 native==soft 2001/2001, KissFFT
12/12, interval IW1. Board mode drives the existing
board scripts and refuses cleanly without toolchain or
board. Fresh-clone gate: git archive + empty cache ran
green end-to-end in 52 s with real downloads.

Planted-copy verification (verifier-w5demo, Spark): NOT
READY on the planted copy as constructed, 5 of 5 caught
(85 of 90 cumulative). MPFR twiddle provenance remains
scratch evidence (the demo proves hash identity, and
says so); board flashing is lead-run after merge.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
EOF
git merge --no-ff wave5-demo -F "$TMPDIR/mm.txt" || exit 1

cat "$WS/scratch/lead/plants-w5demo.jsonl" >> docs/metrics/plants.jsonl
"$MSF_PYTHON" - <<'PYEOF'
import json
n = sum(1 for l in open("docs/metrics/plants.jsonl", encoding="utf-8") if l.strip() and json.loads(l))
print("plants.jsonl OK", n, "rows")
PYEOF
[ $? -eq 0 ] || exit 1
cat > "$TMPDIR/pm.txt" <<'PEOF'
Landed verifier-w5demo plant grades (5 of 5)

85 of 90 cumulative.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
PEOF
git add docs/metrics/plants.jsonl && git commit -F "$TMPDIR/pm.txt" || exit 1
echo "--- smoke on merge tree ---"
bash tools/run.sh smoke; rc=$?
echo "smoke rc=$rc"
git log --oneline -4
exit $rc
