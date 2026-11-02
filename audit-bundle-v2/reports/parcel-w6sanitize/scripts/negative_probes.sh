#!/usr/bin/env bash
# v2: invoke run.sh through $BASH (Git Bash), never bare `bash`
# resolved through an MSYS2-first PATH - that hop drops MSF_*
# environment (run.sh board comment, measured 2026-10-28; hit by
# v1 of this script, logs/neg preserved as that evidence).
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-sanitize || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
GCC64=/c/msys64/mingw64/bin/gcc
D=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6sanitize/logs/neg2
mkdir -p "$D"
fail=0
show() { grep -E 'REFUSED|usage|python:' "$1" > "$1.grep" 2>&1; cat "$1.grep"; }
# 1. MSF_SANITIZE with a non-sanitize budget refused by name
MSF_SANITIZE=trap "$BASH" tools/run.sh standard > "$D/wrong-budget.log" 2>&1; rc=$?
echo "probe wrong-budget: rc=$rc"; show "$D/wrong-budget.log"
[ $rc -eq 2 ] && grep -q REFUSED "$D/wrong-budget.log" || fail=1
# 2. bogus flavour refused by name
MSF_SANITIZE=bogus "$BASH" tools/run.sh sanitize > "$D/bogus.log" 2>&1; rc=$?
echo "probe bogus-flavour: rc=$rc"; show "$D/bogus.log"
[ $rc -eq 2 ] && grep -q REFUSED "$D/bogus.log" || fail=1
# 3. usage line names sanitize; unknown budget refused
"$BASH" tools/run.sh nope > "$D/usage.log" 2>&1; rc=$?
echo "probe usage: rc=$rc :: $(cat "$D/usage.log")"
[ $rc -eq 2 ] && grep -q 'sanitize' "$D/usage.log" || fail=1
# 4. unsanitized twin of the ub canary exits 0: proves the trap in
#    the sanitize run is the instrumentation, not the program
"$GCC64" -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off tests/sanitize_canary_ub.c -o "$D/ub-plain.exe" > "$D/ub-plain-build.log" 2>&1 || fail=1
"$D/ub-plain.exe" > "$D/ub-plain.log" 2>&1; rc=$?
echo "probe ub-unsanitized: rc=$rc :: $(cat "$D/ub-plain.log")"
[ $rc -eq 0 ] && grep -q 'printed = NOT caught' "$D/ub-plain.log" || fail=1
echo "NEGATIVE-PROBES fail=$fail"
exit $fail
