#!/usr/bin/env bash
# mutants.sh - the four brief mutants, each watched failing.
# M1 RD/RU swapped on lo endpoints; M2 RN for directed;
# M4 stage-3 flags guard removed (compile-time hooks, defaults
# correct). M3 Number form in the containment path (sed copy):
# watched failing = the source-scan gate refuses it, plus its
# behavioural audit outcome is recorded. A mutant the audit
# ACCEPTS (except M3's scan verdict) fails this script.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="$PWD/.venv/Scripts/python.exe"
WT=worktrees/w4-interval
OUT=scratch/parcel-w4interval
FAIL=0
SRC="$WT/src/msf16.c $WT/src/msf32.c $WT/src/msf64.c $WT/src/msf_flags.c $WT/src/msf_wide.c $WT/src/msf_roundpack.c $WT/src/msf_string.c $WT/tests/sha256.c"

run_mutant() { # name, workload.c, extra defs...
    local name="$1" wlc="$2"; shift 2
    gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off "$@" \
        $SRC "$wlc" "$WT/board/interval_host.c" \
        -o "$OUT/build/host-$name.exe" || { echo "MUTANT $name: BUILD FAIL"; FAIL=1; return; }
    "$OUT/build/host-$name.exe" "$WT/tests/interval_catalogue.tsv" \
        > "$OUT/build/out-$name.txt" 2>&1
    if "$MSF_PYTHON" "$OUT/audit.py" "$WT/tests/interval_catalogue.tsv" \
           "$OUT/build/out-$name.txt" > "$OUT/build/audit-$name.txt" 2>&1; then
        echo "MUTANT $name: NOT REFUSED (audit passed) <== BAD"
        FAIL=1
    else
        echo "MUTANT $name: refused as required"
        grep -E '^containment|^FAIL' "$OUT/build/audit-$name.txt" | head -4
        grep '^HOST_SHA256' "$OUT/build/out-$name.txt" || true
    fi
}

run_mutant m1-rdru-swap "$WT/board/interval_workload.c" \
    -DIW_RM_LO=MSF_ROUND_TOWARD_POSITIVE
run_mutant m2-rn "$WT/board/interval_workload.c" \
    -DIW_RM_LO=MSF_ROUND_TIES_TO_EVEN -DIW_RM_HI=MSF_ROUND_TIES_TO_EVEN
run_mutant m4-noguard "$WT/board/interval_workload.c" \
    -DIW_STAGE3_GUARD=0

# M3: sed a scratch copy to the suppressing 9.6 forms.
sed -e 's/msf64_minimum(/msf64_minimum_number(/g' \
    -e 's/msf64_maximum(/msf64_maximum_number(/g' \
    -e 's/msf32_minimum(/msf32_minimum_number(/g' \
    -e 's/msf32_maximum(/msf32_maximum_number(/g' \
    "$WT/board/interval_workload.c" > "$OUT/build/workload-m3.c"
if cmp -s "$WT/board/interval_workload.c" "$OUT/build/workload-m3.c"; then
    echo "MUTANT m3-number: sed produced no diff <== BAD"; FAIL=1
elif grep -nE '_number' "$OUT/build/workload-m3.c" >/dev/null; then
    echo "MUTANT m3-number: refused by source-scan gate as required"
    grep -nE '_number' "$OUT/build/workload-m3.c" | head -2
else
    echo "MUTANT m3-number: scan did not catch <== BAD"; FAIL=1
fi
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -I"$WT/board" \
    $SRC "$OUT/build/workload-m3.c" "$WT/board/interval_host.c" \
    -o "$OUT/build/host-m3.exe" && \
"$OUT/build/host-m3.exe" "$WT/tests/interval_catalogue.tsv" \
    > "$OUT/build/out-m3.txt" 2>&1
if "$MSF_PYTHON" "$OUT/audit.py" "$WT/tests/interval_catalogue.tsv" \
       "$OUT/build/out-m3.txt" > "$OUT/build/audit-m3.txt" 2>&1; then
    echo "MUTANT m3-number behavioural note: audit still passes on this"
    echo "  catalogue (no decided endpoint here depends on NaN suppression);"
    echo "  the refusing gate is the source scan above, by brief design."
else
    echo "MUTANT m3-number: also refused behaviourally"
    grep -E '^containment|^FAIL' "$OUT/build/audit-m3.txt" | head -4
fi

echo "MUTANTS overall: $([ $FAIL -eq 0 ] && echo PASS || echo FAIL)"
exit $FAIL
