#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export TMPDIR=$PWD/build/smoke/tmp
mkdir -p "$TMPDIR"
echo "start $(date -Iseconds)"
time bash tools/run.sh smoke > build/w1/logs/run-smoke-1.log 2>&1
rc=$?
echo "smoke rc=$rc end $(date -Iseconds)"
cat build/w1/logs/run-smoke-1.log
exit $rc
