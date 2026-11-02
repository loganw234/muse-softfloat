#!/bin/bash
# Final checks: verifier-row annotations, tree cleanliness, full file hashes.
set -u
DUP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/dup"
OUT="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
cd "$DUP"
echo "=== appended verifier rows carry a/b/verdict/sent_back ==="
"$MSF_PYTHON" -c "
import json
rows=[json.loads(l) for l in open('$OUT/app-passes.jsonl')]
v=[r for r in rows if r.get('role')=='verifier']
print('verifier rows:',len(v))
missing=[r['agent'] for r in v if not all(k in r for k in ('a','b','verdict','sent_back'))]
print('missing annotation keys:',missing)
print('verdicts:',sorted(set(r.get('verdict') for r in v)))
a=[r for r in rows if r.get('role') in ('author','fixer')]
print('author/fixer rows:',len(a),'all have commit:',all('commit' in r for r in a))
s=[r for r in rows if r.get('role')=='surveyor']
print('surveyor rows:',len(s))
"
echo "=== duplicate status (tracked only) ==="
git status --short | grep -v '^??' | head -5; echo "(end status)"
echo "=== copy status (read-only check) ==="
git -C "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify6-metrics" status --short | head -5; echo "(end copy status)"
echo "=== full-sha256 parent prefix files ==="
sha256sum "$OUT"/parent-*.jsonl
