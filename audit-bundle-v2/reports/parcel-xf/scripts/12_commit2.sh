#!/usr/bin/env bash
set -uo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/parcel-xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-xf\tmp'
export TEMP="$TMP"
cd "$ROOT/worktrees/w2-xf" || exit 9
G="git -c safe.directory=$PWD"
$G add src/msf32.c
printf '%s\n\n%s\n\n%s\n' \
  "Reword an msf32.c comment the smoke type scan refused" \
  "The scan greps whole words for hardware arithmetic type names in src/ and include/; the Wave 2 header comment used such a word inside a hyphenated compound about rounding twice. Comment-only change, no code differs. Smoke after the fix: PASS (52,168 committed vectors, 9/9 negative controls refused, drift clean)." \
  "Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>" > "$ROOT/scratch/parcel-xf/commit2.txt"
$G commit -F "$ROOT/scratch/parcel-xf/commit2.txt"
echo "commit exit=$?"
$G log --oneline -3
$G status --porcelain
