#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
PY=.venv/Scripts/python.exe
$PY softfloat-bootstrap-kit/tools/plant.py check --key scratch/lead/keys/key-9a414ec.json --repo muse-softfloat --copy worktrees/verify2-f16 --dispatch || exit 1
$PY softfloat-bootstrap-kit/tools/plant.py check --key scratch/lead/keys/key-5f41c0c.json --repo muse-softfloat --copy worktrees/verify2-xf --dispatch || exit 1
echo "DISPATCH CHECKS PASS"
