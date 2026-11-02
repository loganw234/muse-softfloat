#!/usr/bin/env bash
# auditor-adherence-2 counting runner: Git Bash, MSF_PYTHON pinned, TMP in scratch.
set -u
cd "$(dirname "$0")/../.." || exit 2
export MSF_PYTHON="$PWD/.venv/Scripts/python.exe"
mkdir -p scratch/audit-adherence-2/tmp
export TMPDIR="$PWD/scratch/audit-adherence-2/tmp"
export TMP="$(cygpath -m "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
PY="$MSF_PYTHON"
echo "python: $PY"; "$PY" --version
for s in git_audit metrics_ledger_audit claims_tree_audit brief_scratch_audit; do
  echo "######## $s"
  "$PY" "scratch/audit-adherence-2/$s.py" > "scratch/audit-adherence-2/$s.out.txt" 2>&1
  echo "exit=$? lines=$(wc -l < scratch/audit-adherence-2/$s.out.txt)"
done
