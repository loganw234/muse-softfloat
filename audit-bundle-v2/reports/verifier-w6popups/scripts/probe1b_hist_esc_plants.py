"""Probe1b: merges (history.json), escalations filings, plants mechanical totals."""
import json, sys
from pathlib import Path
from collections import Counter
DUP = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
seg = DUP / "video/segments"

hist = json.load(open(seg / "history.json", encoding="utf-8"))
print("history keys:", list(hist.keys()))
merges = hist.get("merges", [])
print("n merges in history.json:", len(merges))
print("merge keys sample:", list(merges[0].keys()) if merges else None)
print("commit_count_all:", hist.get("commit_count_all"))
print("gate_anchors:", json.dumps(hist.get("gate_anchors")))
# node_events / popup sources?
print("n node_events:", len(hist.get("node_events", [])))

esc = [json.loads(l) for l in open(DUP / "docs/metrics/escalations.jsonl", encoding="utf-8") if l.strip()]
print("escalation filings total:", len(esc))
print("filing keys:", sorted({k for r in esc for k in r.keys()}))
waves = Counter(str(r.get("wave", "?")) for r in esc)
print("filings by wave:", dict(sorted(waves.items())))
print("first filing:", json.dumps(esc[0])[:300])
print("last filing:", json.dumps(esc[-1])[:300])

# FENCED FILE: mechanical totals only (no row contents)
pl = (DUP / "docs/metrics/plants.jsonl").read_text(encoding="utf-8").splitlines()
rows = [l for l in pl if l.strip()]
print("plants.jsonl mechanical lines:", len(rows))
grades = Counter()
for l in rows:
    try:
        g = json.loads(l).get("grade", "<NO-GRADE-KEY>")
    except Exception as e:
        g = "<UNPARSEABLE>"
    grades[str(g)] += 1
print("plants.jsonl grade values:", dict(grades))
