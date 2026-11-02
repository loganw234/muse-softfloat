#!/usr/bin/env bash
# Build Wave 2 planted verification copies. Run via Git Bash from workspace root.
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
command -v git || { echo "git not on PATH"; exit 1; }
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR"
PY=.venv/Scripts/python.exe
BASE=dd48b08c7cb2f1aa957d15972d919c6d3051ad78
$PY softfloat-bootstrap-kit/tools/plant.py make --repo muse-softfloat --base $BASE \
  --key scratch/lead/keys/w2-f16-draft.json --out worktrees/verify2-f16 || exit 1
$PY softfloat-bootstrap-kit/tools/plant.py make --repo muse-softfloat --base $BASE \
  --key scratch/lead/keys/w2-xf-draft.json --out worktrees/verify2-xf || exit 1
echo "--- dispatch checks ---"
for k in scratch/lead/keys/key-*.json; do
  case "$k" in *1779df0*|*d1e9442*) continue;; esac
  echo "key: $k"; $PY softfloat-bootstrap-kit/tools/plant.py check "$k" --dispatch || exit 1
done
sha256sum scratch/lead/keys/key-*.json
