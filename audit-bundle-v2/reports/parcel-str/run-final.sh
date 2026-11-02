#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
S=$ROOT/scratch/parcel-str
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=$S/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
cd "$W" || exit 9
git -c safe.directory="$W" log --oneline -1
git -c safe.directory="$W" status --porcelain | head -3
CFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"
gcc $CFLAGS -DMSF_BUILD_ID='"final-8712ec1"' src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c tests/runner.c tests/sha256.c -o build/str/msf_runner_final.exe
echo "final build rc=$?"
build/str/msf_runner_final.exe verify tests/vectors/from-decimal-str.vec tests/vectors/from-hex-str.vec tests/vectors/to-decimal-str.vec tests/vectors/to-hex-str.vec > "$S/final-directed.log" 2>&1
echo "final directed rc=$?"
grep -E '^(total|VERDICT)' "$S/final-directed.log"
# drift of the committed tree
python tools/gen_tables.py "$S/tmp/gencheck" > /dev/null 2>&1
for f in include/muse_softfloat.h src/msf_formats.h tests/msf_dispatch.h docs/COVERAGE.tsv; do
  cmp -s "$f" "$S/tmp/gencheck/$f" && echo "drift clean: $f" || echo "DRIFT: $f"
done
