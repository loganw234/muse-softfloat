#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../../worktrees/w6-examples" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/msys64/mingw64/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/../../scratch/lead/tmp" TMP="$(cygpath -w "$PWD/../../scratch/lead/tmp")" TEMP="$TMP"
mkdir -p "$TMPDIR"
bash examples/host/build.sh
echo "example rc=$?"
