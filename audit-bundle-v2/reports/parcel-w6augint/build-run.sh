#!/usr/bin/env bash
# build-run.sh LABEL [extra gcc args...] - run from worktree root.
set -u
LABEL="$1"; shift
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
WS=/c/Users/logan/source/repos/Muse-Softfloat
SCR=$WS/scratch/parcel-w6augint
export MSF_PYTHON=$WS/.venv/Scripts/python.exe
mkdir -p "$SCR/build" "$SCR/tmp"
export TMPDIR=$SCR/tmp
export TMP="$(cygpath -w "$SCR/tmp")"
export TEMP="$TMP"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off "$@" $SRC tests/sha256.c board/interval_workload.c board/interval_host.c -o "$SCR/build/interval_host-$LABEL.exe" > "$SCR/build/build-$LABEL.log" 2>&1 || { cat "$SCR/build/build-$LABEL.log"; echo "BUILD $LABEL FAILED"; exit 1; }
"$SCR/build/interval_host-$LABEL.exe" tests/interval_catalogue.tsv > "$SCR/stream-$LABEL.txt" 2> "$SCR/stream-$LABEL.err"
rc=$?
echo "run $LABEL rc=$rc"
grep -E '^(SUMMARY|HOST_SHA256)' "$SCR/stream-$LABEL.txt" || true
wc -l "$SCR/stream-$LABEL.txt"
exit $rc
