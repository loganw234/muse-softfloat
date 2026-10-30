#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
PY=.venv/Scripts/python.exe
$PY softfloat-bootstrap-kit/tools/plant.py check --key scratch/lead/keys/key-f58f299.json --repo muse-softfloat --copy worktrees/verify3-str --dispatch > scratch/lead/check-w3.log 2>&1 && echo "DISPATCH CHECK PASS" || { tail -3 scratch/lead/check-w3.log; exit 1; }
