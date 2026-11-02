#!/usr/bin/env bash
# Fixer timing-equality dump: import gitvisual in the worktree after the
# two-card fix, compare the first 11 lines against the parcel's base dump.
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-popups
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
"$MSF_PYTHON" /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6popups/dump_timings.py > /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6popups/fix_after_timings.txt
echo "--- first-11-lines diff vs base (empty = identical) ---"
diff <(head -n 11 /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6popups/before_timings.txt) <(head -n 11 /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6popups/fix_after_timings.txt) && echo TIMING_EQUALITY_PASS
echo "--- POPUP5 copy section diff vs parcel after-dump (expect only the 2 fixed cards) ---"
diff /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6popups/after_timings.txt /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6popups/fix_after_timings.txt; true
