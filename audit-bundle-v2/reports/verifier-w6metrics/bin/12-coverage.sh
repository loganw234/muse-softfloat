#!/bin/bash
# Probe 5: coverage — briefed agents vs rowed agents.
set -u
ROOT="C:/Users/logan/source/repos/Muse-Softfloat"
DUP="$ROOT/scratch/verifier-w6metrics/dup"
OUT="$ROOT/scratch/verifier-w6metrics/out"
export MSF_PYTHON="$ROOT/.venv/Scripts/python.exe"
cd "$DUP"
echo "=== all Role: agents in workspace ledger/briefs ==="
grep -h '^\*\*Role:\*\*' "$ROOT"/ledger/briefs/*.md | sed 's/\*\*Role:\*\* //' | sort -u
echo "=== appended usage agents ==="
"$MSF_PYTHON" -c "
import json
rows=[json.loads(l) for l in open('$OUT/app-usage.jsonl')]
print(len(rows))
print('\n'.join(sorted(r['agent'] for r in rows)))
"
echo "=== frozen usage agents count ==="
"$MSF_PYTHON" -c "
import json
rows=[json.loads(l) for l in open('$OUT/parent-usage.jsonl')]
print(len(rows))
"
