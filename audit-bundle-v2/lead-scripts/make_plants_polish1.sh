#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
command -v git || { echo "git not on PATH"; exit 1; }
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR"
PY=.venv/Scripts/python.exe
$PY softfloat-bootstrap-kit/tools/plant.py make --repo muse-softfloat --base 400b271 \
  --key scratch/lead/keys/polish-stale1-draft.json --out worktrees/verify-polish1 || exit 1
KEY=$(ls -t scratch/lead/keys/key-*.json | head -n 1)
echo "KEYFILE $KEY"
$PY softfloat-bootstrap-kit/tools/plant.py check --key "$KEY" --repo muse-softfloat --copy worktrees/verify-polish1 --dispatch || exit 1
$PY softfloat-bootstrap-kit/tools/plant.py hash "$KEY"
