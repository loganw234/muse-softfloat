#!/usr/bin/env bash
# verifier-w164 (3b): replay exact-w164 probe through the copy's runner.
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/w1v/tmp
export TMPDIR=$PWD/build/w1v/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f64
LOG=$SCR/v-exact-run.log
build/smoke/msf_runner.exe verify "$SCR"/exact-tmp/w164-*.vec > "$LOG" 2>&1
echo "exact rc=$?"
grep -E "^(file|prov|total|VERDICT)" "$LOG"
echo "--- FAILs by file ---"
grep "^FAIL" "$LOG" | sed 's|.*exact-tmp/||;s|\.vec:.*| |' | awk '{print $1}' | sort | uniq -c
