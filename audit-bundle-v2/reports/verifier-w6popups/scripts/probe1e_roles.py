"""Probe1e: recount lane roles from episodes; spine identity; STUDY_LABELS size."""
import json, sys
from pathlib import Path
from collections import Counter
DUP = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
pg = json.load(open(DUP / "video/segments/process_graph.json", encoding="utf-8"))
eps = pg["episodes"]
lanes = [e for e in eps if e.get("kind") == "lane"]
spine = [e for e in eps if e.get("kind") != "lane"]
print("lanes:", len(lanes), "non-lane:", len(spine))
print("drawn lane roles:", dict(Counter(e.get("role") for e in lanes)))
print("lane agent-role pairs (role, agent):")
for e in lanes:
    pass
print("spine episodes:", json.dumps(spine)[:600])
# passes-role distribution: check for passes_role / passes fields
keys = sorted({k for e in eps for k in e.keys()})
print("episode keys:", keys)
pr = Counter(e.get("passes_role", e.get("role")) for e in eps)
print("passes_role-or-role:", dict(pr))
# STUDY_LABELS replication (same predicate as gitvisual.py)
sl = {e["id"] for e in lanes if e["role"] == "surveyor" and (
    e["agent"].startswith(("study-tier2", "study-sf2")) or "SF-0" in e["work"])}
print("STUDY_LABELS count:", len(sl))
print("surveyor agents:", sorted({e["agent"] for e in lanes if e["role"] == "surveyor"})[:40])
print("n surveyor lanes:", sum(1 for e in lanes if e["role"] == "surveyor"))
print("verifier lanes:", sum(1 for e in lanes if e["role"] == "verifier"))
print("author lanes:", sum(1 for e in lanes if e["role"] == "author"))
print("fixer lanes:", [(e["id"], e["agent"]) for e in lanes if e["role"] == "fixer"])
print("lead lanes:", [(e["id"], e["agent"]) for e in lanes if e["role"] == "lead"])
