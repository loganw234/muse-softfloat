#!/bin/bash
# Probe D: precise regen diff regions.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT" || exit 9
C=worktrees/verify4-trig/src/msf_trig_tables.h
R=scratch/verifier-w4trig/tmp/trig-regen.h
echo "--- sizes ---"
wc -c "$C" "$R"
echo "--- EK lines ---"
grep -n 'EK_EXP' "$C" "$R"
echo "--- first SIN entries, committed vs regen ---"
grep -n '1/1!' "$C" | head -2
grep -n '1/1!' "$R" | head -2
echo "--- unified diff (first 40) ---"
diff "$C" "$R" | head -40
echo "--- diff line count ---"
diff "$C" "$R" | wc -l
