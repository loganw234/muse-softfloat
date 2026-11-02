#!/usr/bin/env bash
# smoke then standard (merge gates), MSF_PYTHON pinned.
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT/worktrees/w5-log2"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="$ROOT/.venv/Scripts/python.exe"
export TMPDIR="$ROOT/scratch/parcel-w5log2/tmp"
mkdir -p "$TMPDIR"
ulimit -v 4194304 2>/dev/null || true
S="$ROOT/scratch/parcel-w5log2"
bash tools/run.sh smoke > "$S/smoke.log" 2>&1
echo "smoke rc=$?"
tail -5 "$S/smoke.log"
bash tools/run.sh standard > "$S/standard.log" 2>&1
echo "standard rc=$?"
tail -5 "$S/standard.log"
