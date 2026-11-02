"""Probe1a: dump process_graph.json accounting + role structure (duplicate tree only)."""
import json, sys
from pathlib import Path
DUP = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
pg = json.load(open(DUP / "video/segments/process_graph.json", encoding="utf-8"))
print("PG top keys:", list(pg.keys()))
print("--- accounting ---")
print(json.dumps(pg["accounting"], indent=1))
eps = pg["episodes"]
print("n episodes:", len(eps))
from collections import Counter
print("kinds:", Counter(e.get("kind") for e in eps))
lanes = [e for e in eps if e.get("kind") == "lane"]
print("n lanes:", len(lanes))
print("lane roles:", Counter(e.get("role") for e in lanes))
print("lane agents sample:", sorted({e.get("agent") for e in lanes})[:10])
nonlane = [e for e in eps if e.get("kind") != "lane"]
print("non-lane kinds:", Counter(e.get("kind") for e in nonlane))
print("non-lane roles:", Counter(e.get("role") for e in nonlane))
spine = [e for e in eps if e.get("kind") != "lane" or "spine" in json.dumps(e).lower()]
print("spine-ish count:", len(spine))
# passes roles? check for by_passes keys anywhere
def find_keys(o, prefix, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if k.startswith(prefix):
                out.append((k, v if not isinstance(v, (dict, list)) else type(v).__name__))
            find_keys(v, prefix, out)
    elif isinstance(o, list):
        for v in o:
            find_keys(v, prefix, out)
out = []
find_keys(pg, "by_", out)
print("by_* keys:", out)
out2 = []
find_keys(pg, "pass", out2)
print("pass* keys:", out2[:20])
