#!/usr/bin/env bash
# Reveal-time plant check for verifier-w4minmax (lead only).
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR"
PY=.venv/Scripts/python.exe
KEY=scratch/lead/keys/key-ddb809a.json
$PY softfloat-bootstrap-kit/tools/plant.py check --key "$KEY" --repo muse-softfloat \
  --copy worktrees/verify4-minmax \
  --sha256 0483c3c40ea64d9b94bc5b4d92e17f6de7cc2ddfbd3b95269a95d5d10ab4422a \
  > scratch/lead/check-w4minmax.log 2>&1 && echo "REVEAL CHECK PASS" || { tail -5 scratch/lead/check-w4minmax.log; exit 1; }
$PY softfloat-bootstrap-kit/tools/plant.py list "$KEY" --report scratch/verifier-w4minmax/report.md
