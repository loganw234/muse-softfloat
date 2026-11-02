#!/usr/bin/env bash
# s11_runsh.sh - the copy's own gates, unmodified: smoke, then standard
# only if smoke passes. Memory ceiling inherited; MSF_PYTHON pinned.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-$(pwd)/.venv/Scripts/python.exe}"
export TMPDIR="$(pwd)/scratch/verifier-w5alg2/tmp"
export TMP="$TMPDIR" TEMP="$TMPDIR"
mkdir -p "$TMPDIR" scratch/verifier-w5alg2/out
ulimit -v 4194304
OUT=scratch/verifier-w5alg2/out
{
echo "=== smoke ==="
(cd worktrees/verify5-alg2 && bash tools/run.sh smoke) > $OUT/s11_smoke.log 2>&1
echo "smoke rc=$?"
tail -15 $OUT/s11_smoke.log
if [ "${1:-}" = "standard-too" ]; then
  echo "=== standard ==="
  (cd worktrees/verify5-alg2 && bash tools/run.sh standard) > $OUT/s11_standard.log 2>&1
  echo "standard rc=$?"
  tail -8 $OUT/s11_standard.log
fi
} 2>&1 | tee $OUT/s11_runsh.log
