#!/usr/bin/env bash
# Reveal-time plant check for verifier-w4trig (lead only).
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
export PYTHONIOENCODING=utf-8
mkdir -p "$TMPDIR"
PY=.venv/Scripts/python.exe
KEY=scratch/lead/keys/key-0bfd726.json
$PY softfloat-bootstrap-kit/tools/plant.py check --key "$KEY" --repo muse-softfloat \
  --copy worktrees/verify4-trig \
  --sha256 ec0d8227f3af5cb748b0dfc8e4134d321b62ec3c7d04457cfea5e0ccef3325b0 \
  > scratch/lead/check-w4trig.log 2>&1 && echo "REVEAL CHECK PASS" || { tail -5 scratch/lead/check-w4trig.log; exit 1; }
$PY softfloat-bootstrap-kit/tools/plant.py list "$KEY" --report scratch/verifier-w4trig/report.md
