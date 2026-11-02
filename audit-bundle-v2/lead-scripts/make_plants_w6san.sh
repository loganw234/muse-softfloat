#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
command -v git || { echo "git not on PATH"; exit 1; }
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR"
PY=.venv/Scripts/python.exe
$PY softfloat-bootstrap-kit/tools/plant.py make --repo muse-softfloat --base 537b08e \
  --key scratch/lead/keys/w6-sanitize-draft.json --out worktrees/verify6-sanitize || exit 1
KEYS=$(ls -t scratch/lead/keys/key-*.json | head -n 1)
echo "KEYS $KEYS"
$PY softfloat-bootstrap-kit/tools/plant.py check --key "$KEYS" --repo muse-softfloat --copy worktrees/verify6-sanitize --dispatch || exit 1
$PY softfloat-bootstrap-kit/tools/plant.py hash "$KEYS"
