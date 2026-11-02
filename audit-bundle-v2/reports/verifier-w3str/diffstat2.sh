#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/worktrees/verify3-str" || exit 9
G="git -c safe.directory=$R/worktrees/verify3-str"
echo "=== commits 548a1b9..HEAD:"
$G log --format='%h %ad %s' --date=short 548a1b9..HEAD
echo
echo "=== run.sh + board diffs:"
$G diff 548a1b9..HEAD -- tools/run.sh board/CMakeLists.txt board/run_board.sh
