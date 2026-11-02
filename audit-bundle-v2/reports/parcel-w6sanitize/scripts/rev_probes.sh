#!/usr/bin/env bash
# Revision probes: (E) byte-equivalence old vs new idiom;
# (F) full-SANFLAGS build exactly as build_host does it, plus
# compile-only isolation. Logs under scratch logs/rev/.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
W=/c/Users/logan/source/repos/Muse-Softfloat
S=$W/scratch/parcel-w6sanitize
mkdir -p "$S/logs/rev" "$S/logs/rev/tmp"
export TMPDIR="$S/logs/rev/tmp"
export TMP="$(cygpath -w "$TMPDIR")"; export TEMP="$TMP"
CFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"
SANFLAGS_FULL="-fsanitize=address,undefined -fno-sanitize-recover=all"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"

echo "== E: equivalence probe =="
gcc $CFLAGS "$S/scripts/equiv_probe.c" -o "$S/logs/rev/equiv_probe.exe" > "$S/logs/rev/equiv-build.log" 2>&1
echo "equiv build rc=$?"; cat "$S/logs/rev/equiv-build.log"
"$S/logs/rev/equiv_probe.exe" > "$S/logs/rev/equiv.log" 2>&1
echo "equiv run rc=$?"; cat "$S/logs/rev/equiv.log"

cd "$W/worktrees/w6-sanitize" || exit 9
echo "== F1: full SANFLAGS one-shot build (build_host shape) =="
gcc $CFLAGS $SANFLAGS_FULL -DMSF_BUILD_ID='"rev-fullflags-probe"' $SRC tests/runner.c tests/sha256.c -o "$S/logs/rev/msf_runner_full.exe" > "$S/logs/rev/fullflags-build.log" 2>&1
echo "F1 rc=$?"; cat "$S/logs/rev/fullflags-build.log"

echo "== F2: full SANFLAGS compile-only (-c) runner.c =="
gcc $CFLAGS $SANFLAGS_FULL -DMSF_BUILD_ID='"rev-fullflags-probe"' -c tests/runner.c -o "$S/logs/rev/runner_full.o" > "$S/logs/rev/fullflags-compileonly.log" 2>&1
echo "F2 rc=$?"; cat "$S/logs/rev/fullflags-compileonly.log"; ls -l "$S/logs/rev/runner_full.o" 2>&1

echo "== F3: explicit -Werror=stringop-truncation compile-only runner.c (plain + full flags) =="
gcc $CFLAGS -Werror=stringop-truncation -c tests/runner.c -o "$S/logs/rev/runner_plain_st.o" > "$S/logs/rev/plain-stringop.log" 2>&1
echo "F3 plain rc=$?"; cat "$S/logs/rev/plain-stringop.log"
gcc $CFLAGS $SANFLAGS_FULL -Werror=stringop-truncation -c tests/runner.c -o "$S/logs/rev/runner_full_st.o" > "$S/logs/rev/full-stringop.log" 2>&1
echo "F3 full rc=$?"; cat "$S/logs/rev/full-stringop.log"
echo "REV_PROBES_DONE"
