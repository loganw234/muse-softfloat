#!/usr/bin/env bash
# Merge wave4-kissfft into main, land fetches+plants rows, run standard gate.
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
command -v git || { echo "git not on PATH"; exit 1; }
WS="$(cd .. && pwd)"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export TMPDIR="$WS/scratch/lead/tmp" TMP="$WS/scratch/lead/tmp" TEMP="$WS/scratch/lead/tmp"
mkdir -p "$TMPDIR"

git status --short --branch
[ -z "$(git status --porcelain)" ] || { echo "dirty tree - stop"; exit 1; }

cat > "$TMPDIR/merge-msg.txt" <<'EOF'
Merged SF-1 Step 2c workload: KissFFT Fork B runtime twiddles

Merges wave4-kissfft (d322d07): compat wrappers __wrap_sinpi /
__wrap_cospi / __wrap_floor (binary64; earned by the double
KissFFT link), guarded msf_kissfft firmware target, board host
+ run script, and the BOARD.md protocol entry. KissFFT itself
never enters the repo: fresh-extracted BSD-3 131.2.0 in
scratch, Fork-B-patched at exactly 3 sites (kiss_fft.c and
kiss_fftr.c alloc phases hand exact cycle fractions to
sinpi/cospi - the one named change), double config via the
documented -Dkiss_fft_scalar=double override.

Host proof: 12 configurations (N=256/1024/4096 x complex/real x
fwd/inv) bit-stable across rebuilds; MPFR twiddle-provenance
gate 8,856 fields, 0 mismatches (N=1024 exhaustive incl. fftr
super-twiddles); negative controls watched (1-ulp flip moves
only the targeted row; radian/libm differs 12/12;
contract=fast diverges 12/12 with FMA).

Planted-copy verification (verifier-w4kissfft, Spark): NOT
READY on the planted copy as constructed, 5 of 5 plants
caught (49 of 50 cumulative), no non-plant defect; its
independent rebuild reproduced the provenance gate at the
gated power-of-two sizes. Exactness claim stays qualified:
correctly rounded twiddles at the gated sizes under the named
patch, never "unmodified KissFFT".

Remaining: on-silicon bit-identity run after this merge.

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
EOF
git merge --no-ff wave4-kissfft -F "$TMPDIR/merge-msg.txt" || exit 1

# fetches row (proposed verbatim in the parcel report)
cat >> docs/metrics/fetches.jsonl <<'EOF'
{"name": "KissFFT", "url": "https://github.com/mborgerding/kissfft/archive/refs/tags/131.2.0.tar.gz", "version": "131.2.0", "archive_sha256": "205a8f6a448ef12b091f8ac6a514b5091bb5f6b0b543431ed75f673116cf5cbf", "licence": "BSD-3-Clause", "licence_sha256": "4d6bcab46f27d6d0c878e8305d4bdcfe040d52bf6656b9771f04c9fb9902c0ed", "fetched": "2026-10-27", "by": "tier2-kissfft (pinned archive in scratch/tier2-kissfft/; row proposed by parcel-w4kissfft)", "note": "SF-1 Step 2c workload ONLY (SF-0 4.5): fresh-extracted and Fork-B-patched in scratch by script (exact cycle fractions into sinpi/cospi - the one named change), never vendored; host hash proof + MPFR twiddle-provenance gate at scratch/parcel-w4kissfft/"}
EOF

# plants rows for the KissFFT round (key sha256 0cdba979...)
cat >> docs/metrics/plants.jsonl <<'EOF'
{"wave": "wave4", "verifier": "verifier-w4kissfft", "work": "SF-1 Step 2c workload: KissFFT Fork B runtime twiddles", "key_sha256": "0cdba9791351e0a7cdf25ecae9a5fde29ee3f236559dc85e9cdd3ff71bdefc11", "plant": 1, "shape": "sinpi wrapper calls the cosine core entry", "grade": "caught", "graded_by": "lead", "checked_by": "integration", "note": "(b1) MPFR gate 3472/6964 fields mismatched, all sin; selftest +309 sinpi-fl; wrapper-correct rebuild 0"}
{"wave": "wave4", "verifier": "verifier-w4kissfft", "work": "SF-1 Step 2c workload: KissFFT Fork B runtime twiddles", "key_sha256": "0cdba9791351e0a7cdf25ecae9a5fde29ee3f236559dc85e9cdd3ff71bdefc11", "plant": 2, "shape": "firmware input generator constant differs from the host by one", "grade": "caught", "graded_by": "lead", "checked_by": "integration", "note": "(a3) increment ...406 vs ...407; lead confirmed real host_main.c and firmware verbatim identical"}
{"wave": "wave4", "verifier": "verifier-w4kissfft", "work": "SF-1 Step 2c workload: KissFFT Fork B runtime twiddles", "key_sha256": "0cdba9791351e0a7cdf25ecae9a5fde29ee3f236559dc85e9cdd3ff71bdefc11", "plant": 3, "shape": "guarded KissFFT target builds without its scratch tree", "grade": "caught", "graded_by": "lead", "checked_by": "integration", "note": "(a1) if(TRUE) for if(DEFINED MSF_KISSFFT_DIR); configure without the var dies"}
{"wave": "wave4", "verifier": "verifier-w4kissfft", "work": "SF-1 Step 2c workload: KissFFT Fork B runtime twiddles", "key_sha256": "0cdba9791351e0a7cdf25ecae9a5fde29ee3f236559dc85e9cdd3ff71bdefc11", "plant": 4, "shape": "exact-angle twiddle claim widened past the gated sizes", "grade": "caught", "graded_by": "lead", "checked_by": "integration", "note": "(a4) BOARD.md 'at every transform size' for 'at these gated power-of-two sizes'"}
{"wave": "wave4", "verifier": "verifier-w4kissfft", "work": "SF-1 Step 2c workload: KissFFT Fork B runtime twiddles", "key_sha256": "0cdba9791351e0a7cdf25ecae9a5fde29ee3f236559dc85e9cdd3ff71bdefc11", "plant": 5, "shape": "board host compares row counts but not hash contents", "grade": "caught", "graded_by": "lead", "checked_by": "integration", "note": "(a2) 12 fabricated wrong hashes returned PASS rc 0 under a stub serial module"}
EOF

"$MSF_PYTHON" - <<'PYEOF'
import json
for p in ("docs/metrics/fetches.jsonl", "docs/metrics/plants.jsonl"):
    n = 0
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                json.loads(line); n += 1
    print("jsonl OK", p, n, "rows")
PYEOF
[ $? -eq 0 ] || exit 1

cat > "$TMPDIR/rows-msg.txt" <<'EOF'
Landed KissFFT fetches + plants rows at the Step 2c merge

KissFFT 131.2.0 pinned-archive row (scratch-only workload,
never vendored) and the five verifier-w4kissfft plant grades,
all caught (49 of 50 cumulative).

Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>
EOF
git add docs/metrics/fetches.jsonl docs/metrics/plants.jsonl || exit 1
git commit -F "$TMPDIR/rows-msg.txt" || exit 1

echo "--- standard gate on merge tree ---"
bash tools/run.sh standard; rc=$?
echo "standard rc=$rc"
git log --oneline -3
exit $rc
