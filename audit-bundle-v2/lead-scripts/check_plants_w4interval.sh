#!/usr/bin/env bash
# Reveal-time plant check for verifier-w4interval (lead only).
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR"
PY=.venv/Scripts/python.exe
KEY=scratch/lead/keys/key-b577456.json
$PY softfloat-bootstrap-kit/tools/plant.py check --key "$KEY" --repo muse-softfloat \
  --copy worktrees/verify4-interval \
  --sha256 4fd3df3ba40dfce9d11a93677796414e68a7c212bef5f58b84bccbc03a30aa43 \
  > scratch/lead/check-w4interval.log 2>&1 && echo "REVEAL CHECK PASS" || { tail -5 scratch/lead/check-w4interval.log; exit 1; }
$PY softfloat-bootstrap-kit/tools/plant.py list "$KEY" --report scratch/verifier-w4interval/report.md
