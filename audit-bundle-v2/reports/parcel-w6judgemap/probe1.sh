#!/usr/bin/env bash
# parcel-w6judgemap probe 1: host example + demo interval leg (exact demo compile line)
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-judgemap || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
LOG=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6judgemap
echo "python: $MSF_PYTHON"; "$MSF_PYTHON" --version
bash examples/host/build.sh > "$LOG/example.log" 2>&1; echo "example rc=$?"
tail -5 "$LOG/example.log"
# interval leg exactly as demo/run_demo.sh lines 234-242
[ -d /c/msys64/mingw64/bin ] && export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
CC="${MSF_HOST_CC:-gcc}"
mkdir -p build/judgemap-probe/tmp
export TMPDIR=$PWD/build/judgemap-probe/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"; export TEMP="$TMP"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
$CC -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
    $SRC tests/sha256.c board/interval_workload.c board/interval_host.c \
    -o build/judgemap-probe/interval_host.exe > "$LOG/interval-build.log" 2>&1; echo "interval build rc=$?"
build/judgemap-probe/interval_host.exe tests/interval_catalogue.tsv > "$LOG/interval-out.txt" 2>&1; echo "interval run rc=$?"
grep -E "SUMMARY|HOST_SHA256|ops" "$LOG/interval-out.txt" | head -20
echo "want: $(cat demo/expected-interval.txt | grep HOST_SHA256)"
