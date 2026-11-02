#!/usr/bin/env bash
# dump-run.sh - run from worktree root. Builds the scratch
# instrumented copy, runs it over the catalogue, diffs the copy
# against the shipped source, runs the exact oracle check.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
WS=/c/Users/logan/source/repos/Muse-Softfloat
SCR=$WS/scratch/parcel-w6augint
PY=$WS/.venv/Scripts/python.exe
export MSF_PYTHON=$PY
mkdir -p "$SCR/build" "$SCR/tmp"
export TMPDIR=$SCR/tmp
export TMP="$(cygpath -w "$SCR/tmp")"
export TEMP="$TMP"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
$PY "$SCR/make_dump.py" board/interval_workload.c "$SCR/build/interval_workload_dump.c" || exit 1
diff board/interval_workload.c "$SCR/build/interval_workload_dump.c" > "$SCR/build/dump-instrumentation.diff"; echo "instrumentation diff lines: $(wc -l < "$SCR/build/dump-instrumentation.diff")"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -DIW_DUMP_EXPANSIONS -Iboard $SRC tests/sha256.c "$SCR/build/interval_workload_dump.c" "$SCR/dump_main.c" -o "$SCR/build/dump_host.exe" > "$SCR/build/build-dump.log" 2>&1 || { cat "$SCR/build/build-dump.log"; echo "DUMP BUILD FAILED"; exit 1; }
"$SCR/build/dump_host.exe" tests/interval_catalogue.tsv > "$SCR/dump-out.txt" 2> "$SCR/dump-out.err" || { echo "DUMP RUN FAILED"; exit 1; }
wc -c "$SCR/dump-out.txt"
$PY "$SCR/check_expansions.py" tests/interval_catalogue.tsv "$SCR/dump-out.txt" "$SCR/stream-new.txt"
