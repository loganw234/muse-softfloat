#!/usr/bin/env bash
# Probe 7b: isolated smoke run. Copy the code tree (byte-identical to the
# verify copy's code) into scratch and run tools/run.sh smoke there:
# outside the copy, never modifying the copy (or any live tree).
set -euo pipefail
ulimit -v 4194304 2>/dev/null || true
ulimit -n 4096 2>/dev/null || true
MSF_PYTHON="${MSF_PYTHON:-C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe}"
export MSF_PYTHON
cd "C:/Users/logan/source/repos/Muse-Softfloat"
TREE="scratch/verifier-w5metrics/smoke-tree"
rm -rf "$TREE"
mkdir -p "$TREE"
for d in src include tables tests tools board compat demo site docs; do
  cp -r "muse-softfloat/$d" "$TREE/" 2>/dev/null || echo "(skip $d)"
done
echo "--- docs parity vs verify copy ---"
diff -rq "$TREE/docs" worktrees/verify5-metrics/docs | grep -v metrics | head -5 || true
echo "(docs/metrics differs by design: snapshot predates the refresh)"
cp muse-softfloat/.gitignore muse-softfloat/.gitattributes "$TREE/" 2>/dev/null || true
echo "--- parity of copied tree vs verify copy (code dirs) ---"
diff -rq "$TREE/src" worktrees/verify5-metrics/src && echo SRC-IDENTICAL
diff -rq "$TREE/include" worktrees/verify5-metrics/include && echo INCLUDE-IDENTICAL
diff -rq "$TREE/tables" worktrees/verify5-metrics/tables && echo TABLES-IDENTICAL
diff -q "$TREE/tools/run.sh" worktrees/verify5-metrics/tools/run.sh && echo RUNSH-IDENTICAL
echo "--- tests tree parity (slow) ---"
if diff -rq "$TREE/tests" worktrees/verify5-metrics/tests | head -5; then echo TESTS-IDENTICAL; fi
echo "--- smoke ---"
cd "$TREE"
export MSF_HOST_CC=gcc
bash tools/run.sh smoke 2>&1 | tee "$OLDPWD/scratch/verifier-w5metrics/07b_smoke.log"
echo "SMOKE-EXIT=$?"
