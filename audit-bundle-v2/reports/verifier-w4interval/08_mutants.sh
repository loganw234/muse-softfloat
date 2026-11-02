#!/usr/bin/env bash
# 08_mutants.sh - mutant builds on scratch copies + positive counterparts.
# Each mutant is WATCHED FAILING against the independent audit (03_audit.py);
# the positive counterpart (correct mode) must pass.
set -u
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
COPY="$VROOT/worktrees/verify4-interval"
OUT="$VROOT/scratch/verifier-w4interval"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p "$OUT/mut"
SRCS="$COPY/src/msf16.c $COPY/src/msf32.c $COPY/src/msf64.c $COPY/src/msf_flags.c $COPY/src/msf_wide.c $COPY/src/msf_roundpack.c $COPY/src/msf_string.c"

build_run() { # name, extra -D flags, extra sed-edit flag
  local name="$1" flags="$2"
  # shellcheck disable=SC2086
  gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
    -I"$COPY/include" -I"$COPY/board" $flags \
    $SRCS "$OUT/mut/${name}_workload.c" "$COPY/board/interval_host.c" \
    "$COPY/tests/sha256.c" \
    -o "$OUT/mut/${name}.exe" 2>"$OUT/mut/${name}.blog" || {
    echo "$name BUILD FAILED"; head -20 "$OUT/mut/${name}.blog"; return 1; }
  "$OUT/mut/${name}.exe" "$COPY/tests/interval_catalogue.tsv" \
    > "$OUT/mut/${name}.txt" 2>&1
  echo "$name run rc=$? sha=$(grep HOST_SHA256 "$OUT/mut/${name}.txt")"
}

cp "$COPY/board/interval_workload.c" "$OUT/mut/base_workload.c"
cp "$COPY/board/interval_workload.h" "$OUT/mut/base_workload.h"
# M1: RD/RU swapped on the lo endpoint (lo computed RU)
cp "$COPY/board/interval_workload.c" "$OUT/mut/m1_workload.c"
build_run m1 "-DIW_RM_LO=MSF_ROUND_TOWARD_POSITIVE"
# M2: RN substituted for directed (both sides RN)
cp "$COPY/board/interval_workload.c" "$OUT/mut/m2_workload.c"
build_run m2 "-DIW_RM_LO=MSF_ROUND_TIES_TO_EVEN -DIW_RM_HI=MSF_ROUND_TIES_TO_EVEN"
# M4: exact-stage flags guard removed
cp "$COPY/board/interval_workload.c" "$OUT/mut/m4_workload.c"
build_run m4 "-DIW_STAGE3_GUARD=0"
# P1: positive counterpart - correct RD lo (the documented behaviour)
cp "$COPY/board/interval_workload.c" "$OUT/mut/p1_workload.c"
build_run p1 "-DIW_RM_LO=MSF_ROUND_TOWARD_NEGATIVE"
# M3: Number-form fix copy (minimum_number -> minimum); scan + audit
cp "$COPY/board/interval_workload.c" "$OUT/mut/m3_workload.c"
sed -i 's/msf64_minimum_number/msf64_minimum/' "$OUT/mut/m3_workload.c"
echo "--- M3 fixed copy _number scan (must be clean) ---"
grep -rn "_number" "$OUT/mut/m3_workload.c" || echo "M3 fixed copy: no _number"
build_run m3 "-DIW_RM_LO=MSF_ROUND_TOWARD_NEGATIVE"
echo "--- shipped core _number scan (must FAIL the gate) ---"
grep -c "_number" "$COPY/board/interval_workload.c"

for m in m1 m2 m4 p1 m3; do
  "$MSF_PYTHON" "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4interval/03_audit.py" \
    "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4interval/mut/${m}.txt" "$m" \
    2>&1 | grep -E "^===|VIOLATIONS:|DECIDED-WRONG|FLIPS:|GUARD-NOT|BOX-BAD:|TORUS-BAD:|TSV-EXACT"
done
echo "--- M4 guard rows (s3 must be watched) ---"
grep -E "^RAY.*fam=guard" "$OUT/mut/m4.txt" | cut -c1-200
