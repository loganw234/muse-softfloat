#!/usr/bin/env bash
# gates.sh - Step 1c brief gates beyond the containment audit:
# regeneration identity, source scans, tolerance monotonicity,
# op-cap behaviour. Mutants live in mutants.sh.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="$PWD/.venv/Scripts/python.exe"
WT=worktrees/w4-interval
OUT=scratch/parcel-w4interval
FAIL=0
note() { echo "GATE $1: $2"; [ "$2" = PASS ] || FAIL=1; }

# 1. containment audit on the primary run
if "$MSF_PYTHON" "$OUT/audit.py" "$WT/tests/interval_catalogue.tsv" \
       "$OUT/host-out.txt" > "$OUT/audit-out.txt" 2>&1; then
    note containment-audit PASS
else
    note containment-audit FAIL; cat "$OUT/audit-out.txt"
fi
grep -E '^counts|^naive|^containment' "$OUT/audit-out.txt"

# 2. naive disagreement exhibits present (named in the brief)
for fam in tangent400 limb torus; do
    if grep -q "'$fam': [1-9]" "$OUT/audit-out.txt"; then
        note "naive-disagreement-$fam" PASS
    else
        note "naive-disagreement-$fam" FAIL
    fi
done

# 3. catalogue regeneration byte-identical
"$MSF_PYTHON" "$WT/tests/gen_interval_catalogue.py" "$OUT/build/cat2.tsv" >/dev/null
if cmp -s "$WT/tests/interval_catalogue.tsv" "$OUT/build/cat2.tsv"; then
    note catalogue-regen-byte-identical PASS
else
    note catalogue-regen-byte-identical FAIL
fi

# 4. host hash regeneration byte-identical
"$OUT/build/interval_host.exe" "$WT/tests/interval_catalogue.tsv" > "$OUT/build/host-out2.txt"
if cmp -s "$OUT/host-out.txt" "$OUT/build/host-out2.txt"; then
    note host-hash-regen-byte-identical PASS
else
    note host-hash-regen-byte-identical FAIL
fi

# 5. source scans on the workload core: Number forms banned, no
#    hardware floating type named, no allocation.
scan() { # name, pattern, files...
    local name="$1" pat="$2"; shift 2
    if grep -nE "$pat" "$@" > "$OUT/build/scan.txt" 2>&1; then
        note "$name" FAIL; cat "$OUT/build/scan.txt"
    else
        note "$name" PASS
    fi
}
scan no-number-forms '_number|_magnitude_number' \
    "$WT/board/interval_workload.c" "$WT/board/interval_workload.h"
scan no-hardware-float-types '\b(float|double)\b' \
    "$WT/board/interval_workload.c" "$WT/board/interval_workload.h" \
    "$WT/board/interval_host.c"
scan no-allocation '\b(malloc|calloc|realloc|free)\s*\(' \
    "$WT/board/interval_workload.c"

# 6. torus tolerance halving: UNCERTAIN non-increasing, no flips,
#    brackets nested or equal-first-segment.
"$OUT/build/interval_host.exe" "$WT/tests/interval_catalogue.tsv" \
    --tol-half > "$OUT/build/host-out-half.txt"
if "$MSF_PYTHON" "$OUT/audit.py" "$WT/tests/interval_catalogue.tsv" \
       "$OUT/build/host-out-half.txt" > "$OUT/build/audit-half.txt" 2>&1 && \
   "$MSF_PYTHON" "$OUT/monotonicity.py" "$OUT/host-out.txt" \
       "$OUT/build/host-out-half.txt" > "$OUT/build/mono.txt" 2>&1; then
    note tolerance-halving PASS; cat "$OUT/build/mono.txt"
else
    note tolerance-halving FAIL; cat "$OUT/build/audit-half.txt" "$OUT/build/mono.txt"
fi

# 7. op cap: tiny cap forces UNCERTAIN+caphit on torus rays,
#    and never a decided wrong (audit the capped run too).
"$OUT/build/interval_host.exe" "$WT/tests/interval_catalogue.tsv" \
    --cap 500 > "$OUT/build/host-out-cap.txt"
if grep 'kind=torus' "$OUT/build/host-out-cap.txt" | grep -qv 'caphit=1' && \
   grep 'kind=torus' "$OUT/build/host-out-cap.txt" | grep -qv 'dec=UNCERTAIN'; then
    note op-cap-forces-uncertain FAIL
elif "$MSF_PYTHON" "$OUT/audit.py" "$WT/tests/interval_catalogue.tsv" \
        "$OUT/build/host-out-cap.txt" >/dev/null 2>&1; then
    note op-cap-forces-uncertain PASS
else
    note op-cap-forces-uncertain FAIL
fi
grep 'kind=torus' "$OUT/build/host-out-cap.txt"

echo "GATES overall: $([ $FAIL -eq 0 ] && echo PASS || echo FAIL)"
exit $FAIL
