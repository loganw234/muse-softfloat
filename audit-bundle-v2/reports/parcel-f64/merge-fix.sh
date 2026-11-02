#!/usr/bin/env bash
# usage: merge-fix.sh <lead-fix-commit-hash>
set -euo pipefail
HASH="${1:?need lead fix commit hash}"
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export TMPDIR=$PWD/build/w1/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
G="git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64"
echo "before merge $(date -Iseconds)"
$G status --short
$G log --oneline -3
$G show --name-only --format='%H %s' "$HASH" | head -40
$G merge --no-edit "$HASH"
echo "after merge"
$G log --oneline -4
$G status --short
