#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR"
PY=.venv/Scripts/python.exe
$PY softfloat-bootstrap-kit/tools/plant.py make --repo muse-softfloat \
  --base 548a1b9aa7e71ab988cea77d9f2a1591ca84328e \
  --key scratch/lead/keys/w3-str-draft.json --out worktrees/verify3-str || exit 1
