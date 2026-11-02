import json
from collections import Counter
from pathlib import Path

pg = json.loads(Path("muse-softfloat/video/segments/process_graph.json").read_text(encoding="utf-8"))
eps = pg["episodes"]
for e in eps:
    if e.get("role") == "lead":
        print("spine episode:", {k: e[k] for k in e if k in
              ("id", "agent", "role", "passes_role", "label", "work")})
authors = [e.get("agent") for e in eps if e.get("role") == "author"]
print("author lanes:", len(authors))

esc = [json.loads(l) for l in
       Path("muse-softfloat/docs/metrics/escalations.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
print("escalations by wave:", Counter(e.get("wave") for e in esc))
print("escalations answered values:", Counter(str(e.get("answered"))[:20] for e in esc))
