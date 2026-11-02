#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
command -v git || { echo "git not on PATH"; exit 1; }
WS="$(cd .. && pwd)"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export TMPDIR="$WS/scratch/lead/tmp" TMP="$WS/scratch/lead/tmp" TEMP="$WS/scratch/lead/tmp"
mkdir -p "$TMPDIR"
[ -f "$WS/scratch/lead/plants-w5alg2.jsonl" ] || { echo "plants rows missing"; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "dirty tree - stop"; exit 1; }

cat > "$TMPDIR/mm.txt" <<'EOF'
Merged SF-2 Step 2b: correctly rounded hypot

Merges wave5-alg2 (6566604 + e858498). hypot is exact in a
128-bit anchored window: ordered magnitudes, floor-sum
with a separate tail sticky (never a jam into the sqrt
input - midpoint ties are attainable), sqrt_core scaling,
one pack; specials in Clause 9.2 evaluation order with
inf-over-quiet-NaN, both second-read cells held. Tier 2
is now 45 registered / 45 implemented.

Evidence: 2,500 committed lines per format; binary16
pool sweep 6,553,600 + sampled 1.5M; f32/f64 seeded 1.75M
each, 0 mismatches, every pair three-way cross-decided.
The parcel's jam-mutant equivalence finding (shr_jam is
packed-equivalent to floor+sticky in this realization;
floor shipped as mandated) was independently adjudicated
true by the verifier. cr_hypot corroboration exposed a
foreign FE_UPWARD defect class on this host (6,897
disagreements, all adjudicated MPFR==exact, fenced).

Planted-copy verification (verifier-w5alg2, Spark): NOT
READY on the planted copy as constructed, 5 of 5 caught
(75 of 80 cumulative), no non-plant defect.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
EOF
git merge --no-ff wave5-alg2 -F "$TMPDIR/mm.txt" || exit 1

# VECTORS wording (parcel escalation): mpfr-alg tags now cover hypot too
sed -i 's/Clause 9.2 rSqrt specials/Clause 9.2 rSqrt+hypot specials/; s/rSqrt directed exact\/edge pool/rSqrt+hypot directed exact\/edge pool/; s/rSqrt midpoint-adjacent constructions/rSqrt+hypot midpoint-adjacent constructions/; s/rSqrt seeded finite-positive encoding sweep/rSqrt+hypot seeded sweep/' tests/VECTORS.md
git diff --quiet tests/VECTORS.md && { echo "VECTORS sed no-op - stop"; exit 2; }
cat > "$TMPDIR/vm.txt" <<'VEOF'
Generalised the mpfr-alg tag wording to rSqrt+hypot

Parcel-w5alg2 escalation: the four provenance tag rows
predate hypot, which rides the same tokens.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
VEOF
git add tests/VECTORS.md && git commit -F "$TMPDIR/vm.txt" || exit 1

cat "$WS/scratch/lead/plants-w5alg2.jsonl" >> docs/metrics/plants.jsonl
"$MSF_PYTHON" - <<'PYEOF'
import json
n = sum(1 for l in open("docs/metrics/plants.jsonl", encoding="utf-8") if l.strip() and json.loads(l))
print("plants.jsonl OK", n, "rows")
PYEOF
[ $? -eq 0 ] || exit 1
cat > "$TMPDIR/pm.txt" <<'PEOF'
Landed verifier-w5alg2 plant grades (5 of 5)

75 of 80 cumulative; jam equivalence independently
confirmed (floor==jam packed; floor shipped).

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
PEOF
git add docs/metrics/plants.jsonl && git commit -F "$TMPDIR/pm.txt" || exit 1

echo "--- standard gate on merge tree ---"
bash tools/run.sh standard; rc=$?
echo "standard rc=$rc"
git log --oneline -4
exit $rc
