#!/usr/bin/env bash
# Probe 7b prep: check run.sh build-dir configurability + code parity
# between muse-softfloat snapshot and the verify copy.
set -euo pipefail
cd "C:/Users/logan/source/repos/Muse-Softfloat"
echo "--- build dirs in run.sh ---"
grep -nE 'BUILD|build/|mktemp|TMPDIR|\$\{.*:-' muse-softfloat/tools/run.sh | head -25
echo "--- src listing diff ---"
if diff -rq muse-softfloat/src worktrees/verify5-metrics/src | head -10; then echo SRC-IDENTICAL; fi
echo "--- run.sh diff ---"
if diff -q muse-softfloat/tools/run.sh worktrees/verify5-metrics/tools/run.sh; then echo RUNSH-IDENTICAL; fi
echo "--- tools dir diff ---"
diff -rq muse-softfloat/tools worktrees/verify5-metrics/tools | head -10 || true
echo "--- tables/include/tests diff (names only) ---"
diff -rq muse-softfloat/tables worktrees/verify5-metrics/tables | head -5 || true
diff -rq muse-softfloat/include worktrees/verify5-metrics/include | head -5 || true
