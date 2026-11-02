"""Fixer recounts: parcels lanes vs passes_role; escalations filings by wave."""
import json
from collections import Counter

SEG = "worktrees/w6-popups/video/segments"
MET = "worktrees/w6-popups/docs/metrics"

pg = json.load(open(SEG + "/process_graph.json", encoding="utf-8"))
acc = pg["accounting"]
print("by_role", json.dumps(acc["by_role"]))
print("by_passes_role", json.dumps(acc.get("by_passes_role")))
lanes = [e for e in pg["episodes"] if e["kind"] == "lane"]
print("lane count", len(lanes), "lane roles", dict(Counter(e.get("role") for e in lanes)))
print("lane passes_roles", dict(Counter(e.get("passes_role") for e in lanes)))
for e in pg["episodes"]:
    if e["kind"] == "spine":
        print("spine", {k: e.get(k) for k in ("agent", "role", "passes_role", "kind")})
author_lanes = [e for e in lanes if e.get("role") == "author"]
print("author-role lanes drawn:", len(author_lanes))
spine_as_author = [e for e in pg["episodes"] if e.get("passes_role") == "author"]
print("episodes with passes_role=author:", len(spine_as_author),
      [(e.get("kind"), e.get("agent")) for e in spine_as_author])


def rows(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]

esc = rows(MET + "/escalations.jsonl")
print("escalations filings:", len(esc))
print("by wave:", dict(sorted(Counter(str(r.get("wave", "?")) for r in esc).items())))
print("keys:", sorted(esc[0].keys()))
passes = rows(MET + "/passes.jsonl")
print("passes roles:", dict(Counter(r["role"] for r in passes)))
