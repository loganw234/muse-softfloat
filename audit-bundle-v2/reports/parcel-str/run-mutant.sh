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
PY=$ROOT/.venv/Scripts/python.exe
$PY "$S/make-mutant.py"
grep -c 'MUTANT' "$S/controls/msf_string_mut.c"
cmp -s "$S/controls/msf_string_mut.c" "$S/controls/msf_string_orig.c" && echo "ERROR mutant identical" || echo "mutant differs from orig"
CFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"
gcc $CFLAGS -Isrc -DMSF_BUILD_ID='"mutant"' src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c "$S/controls/msf_string_mut.c" tests/runner.c tests/sha256.c -o "$S/controls/msf_runner_mut.exe"
echo "mutant build rc=$?"
# tie-focused subsets from the committed files
grep -E 'from-dec-ties|from-hex-ties' tests/vectors/from-decimal-str.vec tests/vectors/from-hex-str.vec > "$S/controls/ties.vec" || true
grep -hE 'from-dec-ties|from-hex-ties' tests/vectors/from-decimal-str.vec tests/vectors/from-hex-str.vec > "$S/controls/ties.vec"
wc -l "$S/controls/ties.vec"
"$S/controls/msf_runner_mut.exe" verify "$S/controls/ties.vec" > "$S/controls/mutant.log" 2>&1
echo "mutant-on-ties rc=$? (want nonzero)"
grep -E '^(total|VERDICT)' "$S/controls/mutant.log"
grep '^FAIL' "$S/controls/mutant.log" | head -5 | cut -c1-200
# and the REAL runner passes the same tie file; then revert evidence:
build/str/msf_runner.exe verify "$S/controls/ties.vec" > "$S/controls/ties-real.log" 2>&1
echo "real-on-ties rc=$? (want 0)"
grep -E '^(total|VERDICT)' "$S/controls/ties-real.log"
sha256sum src/msf_string.c "$S/controls/msf_string_orig.c"
cmp src/msf_string.c "$S/controls/msf_string_orig.c" && echo "worktree msf_string.c == pre-mutant copy (mutant never touched it)"
