#!/usr/bin/env bash
# Lead merge-tree check: interval host from muse-softfloat main.
set -eu
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="$PWD/.venv/Scripts/python.exe"
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR" scratch/lead/interval-merge
R=muse-softfloat
OUT=scratch/lead/interval-merge
"$MSF_PYTHON" "$R/tests/gen_interval_catalogue.py" "$OUT/interval_catalogue.tsv"
cmp "$OUT/interval_catalogue.tsv" "$R/tests/interval_catalogue.tsv"
echo "catalogue regen: byte-identical"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
    "$R/src/msf16.c" "$R/src/msf32.c" "$R/src/msf64.c" \
    "$R/src/msf_flags.c" "$R/src/msf_wide.c" "$R/src/msf_roundpack.c" \
    "$R/src/msf_string.c" "$R/tests/sha256.c" \
    "$R/board/interval_workload.c" "$R/board/interval_host.c" \
    -o "$OUT/interval_host.exe"
"$OUT/interval_host.exe" "$R/tests/interval_catalogue.tsv" > "$OUT/host-out.txt"
grep -E '^(rows|ops|IW1|sha256|hash)' "$OUT/host-out.txt" || true
tail -5 "$OUT/host-out.txt"
grep -q 'ce81d66e9b0b0a4b654c4eb82664417780c6f09c3f866901002b286980ba9aec' "$OUT/host-out.txt"
echo "IW1 HASH MATCH"
