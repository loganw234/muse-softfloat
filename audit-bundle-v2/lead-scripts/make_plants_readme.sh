#!/usr/bin/env bash
# Build the README planted verification copy. Git Bash, workspace root.
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
command -v git || { echo "git not on PATH"; exit 1; }
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR"
PY=.venv/Scripts/python.exe
BASE=7ebbe70001fa3a8721db8848cdacb568374ee2d7
$PY softfloat-bootstrap-kit/tools/plant.py make --repo muse-softfloat --base $BASE \
  --key scratch/lead/keys/readme-draft.json --out worktrees/verify-readme || exit 1
echo "--- dispatch check ---"
for k in scratch/lead/keys/key-*.json; do
  case "$k" in *1779df0*|*d1e9442*|*9a414ec*|*5f41c0c*|*f58f299*|*0b2bdc9*|*ddb809a*|*b577456*|*0bfd726*|*cffa42b*) continue;; esac
  echo "key: $k"
  $PY softfloat-bootstrap-kit/tools/plant.py check --key "$k" --repo muse-softfloat --copy worktrees/verify-readme --dispatch || exit 1
  $PY softfloat-bootstrap-kit/tools/plant.py hash "$k"
done
