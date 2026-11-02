#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
command -v git || { echo "git not on PATH"; exit 1; }
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR"
PY=.venv/Scripts/python.exe
$PY softfloat-bootstrap-kit/tools/plant.py make --repo muse-softfloat --base bce49e0 \
  --key scratch/lead/keys/w5-aug-draft.json --out worktrees/verify5-aug || exit 1
for k in scratch/lead/keys/key-*.json; do
  case "$k" in *1779df0*|*d1e9442*|*9a414ec*|*5f41c0c*|*f58f299*|*0b2bdc9*|*ddb809a*|*b577456*|*0bfd726*|*cffa42b*|*ac43737*|*e8122b0*|*2f5e79d*|*dfe5179*|*db941a6*|*6aa816c*|*1e6722d*|*b21510b*|*9fffbb1*|*3e55ff2*|*31a0adc*) continue;; esac
  echo "key: $k"
  $PY softfloat-bootstrap-kit/tools/plant.py check --key "$k" --repo muse-softfloat --copy worktrees/verify5-aug --dispatch || exit 1
  $PY softfloat-bootstrap-kit/tools/plant.py hash "$k"
done
