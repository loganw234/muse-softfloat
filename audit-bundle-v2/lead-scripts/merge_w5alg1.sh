#!/usr/bin/env bash
# Merge wave5-alg1 (+ lead board wiring), plants rows via MSG file, standard.
# PLANTS rows come from $1 (a file with the 5 jsonl lines); abort if absent.
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
command -v git || { echo "git not on PATH"; exit 1; }
WS="$(cd .. && pwd)"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export TMPDIR="$WS/scratch/lead/tmp" TMP="$WS/scratch/lead/tmp" TEMP="$WS/scratch/lead/tmp"
mkdir -p "$TMPDIR"
[ -f "${1:-}" ] || { echo "plants rows file required as \$1"; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "dirty tree - stop"; exit 1; }

cat > "$TMPDIR/mm.txt" <<'EOF'
Merged SF-2 Step 2a: algebraic seam + correctly rounded rSqrt

Merges wave5-alg1 (seam 628a18d, kernel b886e03). The
math_bin signature class lands, r_sqrt + hypot register at
Tier 2 (45 registered; hypot stays planned for Step 2b),
and rSqrt is correctly rounded at all three formats by an
exact integer decision (178-bit logical split compare over
u128 into one pack call, five attributes from birth).
Evidence: binary16 exhaustive 327,680 checks, f32/f64
seeded 1.75M each, 0 mismatches; committed alg vectors
3,595 lines; the fenced rSqrt(-0) = -inf cell is
table-decided (MPFR disagrees and is never sourced for
it). Planted-copy verification (verifier-w5alg1, Spark):
NOT READY on the planted copy as constructed, 4 of 5
caught (70 of 75 cumulative), no non-plant defect - its
own exact decider reproduced the exhaustive gate and the
bounds were re-derived on paper. Board replay follows.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
EOF
git merge --no-ff wave5-alg1 -F "$TMPDIR/mm.txt" || exit 1

# lead board wiring (parcel escalation): msf_alg.c rides the board builds
grep -q 'msf_alg.c' board/CMakeLists.txt || \
  sed -i 's|    ${MSF_ROOT}/src/msf_math.c)|    ${MSF_ROOT}/src/msf_math.c\n    ${MSF_ROOT}/src/msf_alg.c)|' board/CMakeLists.txt
grep -q 'msf_alg.c' board/CMakeLists.txt || { echo "CMake wiring failed"; exit 2; }
grep -q 'msf_alg.c' board/run_board.sh || \
  sed -i 's|src/msf_string.c src/msf_math.c \\|src/msf_string.c src/msf_math.c src/msf_alg.c \\|' board/run_board.sh
grep -q 'msf_alg.c' board/run_board.sh || { echo "run_board wiring failed"; exit 2; }
cat > "$TMPDIR/wm.txt" <<'WEOF'
Wired msf_alg.c into the board builds (Step 2a escalation)

board/CMakeLists.txt MSF_SRC and the run_board.sh host
runner list gain src/msf_alg.c so board budgets link on
the merged tree.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
WEOF
git add board/CMakeLists.txt board/run_board.sh && git commit -F "$TMPDIR/wm.txt" || exit 1

cat "$1" >> docs/metrics/plants.jsonl
"$MSF_PYTHON" - <<'PYEOF'
import json
n = sum(1 for l in open("docs/metrics/plants.jsonl", encoding="utf-8") if l.strip() and json.loads(l))
print("plants.jsonl OK", n, "rows")
PYEOF
[ $? -eq 0 ] || exit 1
cat > "$TMPDIR/pm.txt" <<'PEOF'
Landed verifier-w5alg1 plant grades (4 of 5)

70 of 75 cumulative; the decider-boundary plant was missed
(regeneration agreed anyway - that leg decides nothing in
the shipped sets).

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
PEOF
git add docs/metrics/plants.jsonl && git commit -F "$TMPDIR/pm.txt" || exit 1
echo "--- standard gate on merge tree ---"
bash tools/run.sh standard; rc=$?
echo "standard rc=$rc"
git log --oneline -3
exit $rc
