#!/usr/bin/env bash
# Build the Wave 4 Step 1 planted verification copy. Git Bash, workspace root.
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
command -v git || { echo "git not on PATH"; exit 1; }
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR"
PY=.venv/Scripts/python.exe
BASE=8578114a8bfce73173e484f0d345a87a8ba6d532
$PY softfloat-bootstrap-kit/tools/plant.py make --repo muse-softfloat --base $BASE \
  --key scratch/lead/keys/w4-minmax-draft.json --out worktrees/verify4-minmax || exit 1
echo "--- dispatch check ---"
for k in scratch/lead/keys/key-*.json; do
  case "$k" in *1779df0*|*d1e9442*|*9a414ec*|*5f41c0c*|*f58f299*|*0b2bdc9*) continue;; esac
  echo "key: $k"
  $PY softfloat-bootstrap-kit/tools/plant.py check --key "$k" --repo muse-softfloat --copy worktrees/verify4-minmax --dispatch || exit 1
  $PY softfloat-bootstrap-kit/tools/plant.py hash "$k"
done
