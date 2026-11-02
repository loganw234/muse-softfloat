#!/usr/bin/env bash
# build-run.sh - generate catalogue, build host runner, run it.
# Run under Git Bash from the workspace root.
set -eu
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="$PWD/.venv/Scripts/python.exe"
WT=worktrees/w4-interval
OUT=scratch/parcel-w4interval
mkdir -p "$OUT/build"

"$MSF_PYTHON" "$WT/tests/gen_interval_catalogue.py" "$WT/tests/interval_catalogue.tsv"

gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
    "$WT/src/msf16.c" "$WT/src/msf32.c" "$WT/src/msf64.c" \
    "$WT/src/msf_flags.c" "$WT/src/msf_wide.c" "$WT/src/msf_roundpack.c" \
    "$WT/src/msf_string.c" "$WT/tests/sha256.c" \
    "$WT/board/interval_workload.c" "$WT/board/interval_host.c" \
    -o "$OUT/build/interval_host.exe"
echo "built $OUT/build/interval_host.exe"

"$OUT/build/interval_host.exe" "$WT/tests/interval_catalogue.tsv" \
    > "$OUT/host-out.txt"
tail -5 "$OUT/host-out.txt"
grep 'kind=torus' "$OUT/host-out.txt"
grep 'kind=box' "$OUT/host-out.txt"
grep 'fam=guard' "$OUT/host-out.txt"
echo BUILD-RUN OK
