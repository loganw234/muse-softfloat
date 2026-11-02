#!/bin/bash
# Probe 2: shape + references of appended rows.
set -u
DUP="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/dup"
OUT="C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6metrics/out"
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
cd "$DUP"
# split frozen/appended spans: usage parent 93, passes parent 94, briefs parent 39
head -n 93 docs/metrics/usage.jsonl > "$OUT/frozen-usage.jsonl"
tail -n +94 docs/metrics/usage.jsonl > "$OUT/app-usage.jsonl"
head -n 94 docs/metrics/passes.jsonl > "$OUT/frozen-passes.jsonl"
tail -n +95 docs/metrics/passes.jsonl > "$OUT/app-passes.jsonl"
head -n 39 docs/metrics/briefs.jsonl > "$OUT/frozen-briefs.jsonl"
tail -n +40 docs/metrics/briefs.jsonl > "$OUT/app-briefs.jsonl"
wc -l "$OUT"/app-*.jsonl "$OUT"/frozen-*.jsonl
echo "=== appended passes agents ==="
"$MSF_PYTHON" -c "
import json
rows=[json.loads(l) for l in open('$OUT/app-passes.jsonl')]
print(len(rows))
for r in rows: print(r.get('agent'), '|', r.get('role'), '|', r.get('commit','-'), '|', r.get('verdict','-'), '|', r.get('end','-'))
"
echo "=== appended briefs agents ==="
"$MSF_PYTHON" -c "
import json
rows=[json.loads(l) for l in open('$OUT/app-briefs.jsonl')]
for r in rows: print(json.dumps(r))
"
