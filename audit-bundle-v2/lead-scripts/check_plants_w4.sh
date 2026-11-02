#!/usr/bin/env bash
# Reveal-time plant check for verifier-w4seam (lead only).
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR"
PY=.venv/Scripts/python.exe
KEY=scratch/lead/keys/key-0b2bdc9.json
$PY softfloat-bootstrap-kit/tools/plant.py check --key "$KEY" --repo muse-softfloat \
  --copy worktrees/verify4-seam \
  --sha256 80c99a9bba993b5610f48c1f8050736f013b657f0a0f3a86dd4d5590193d7252 \
  > scratch/lead/check-w4.log 2>&1 && echo "REVEAL CHECK PASS" || { tail -5 scratch/lead/check-w4.log; exit 1; }
$PY softfloat-bootstrap-kit/tools/plant.py list "$KEY" --report scratch/verifier-w4seam/report.md
