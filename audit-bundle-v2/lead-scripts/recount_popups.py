import json
from collections import Counter
from pathlib import Path

SEG = Path("muse-softfloat/video/segments")
pg = json.loads((SEG / "process_graph.json").read_text(encoding="utf-8"))
print("process_graph top-level keys:", sorted(pg.keys())[:20])
for k, v in pg.items():
    if isinstance(v, list) and v and isinstance(v[0], dict) and "role" in v[0]:
        print(f"episodes list {k!r}: n={len(v)} roles={Counter(e['role'] for e in v)}")
    if isinstance(v, dict) and ("accounting" in k or "role" in k):
        print(k, "->", v)
acc = pg.get("accounting")
if acc:
    print("accounting:", json.dumps(acc)[:600])

passes = [json.loads(l) for l in
          Path("muse-softfloat/docs/metrics/passes.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
print("passes.jsonl HEAD rows:", len(passes), "roles:", Counter(p.get("role") for p in passes))
print("passes last 3 agents:", [p.get("agent") for p in passes[-3:]])

esc = [json.loads(l) for l in
        Path("muse-softfloat/docs/metrics/escalations.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
print("escalations.jsonl rows:", len(esc), "keys:", sorted(esc[0].keys()) if esc else None)
for key in ("kind", "type", "status", "to", "outcome"):
    if esc and key in esc[0]:
        print(" esc by", key, Counter(str(e.get(key))[:40] for e in esc))

hist = json.loads((SEG / "history.json").read_text(encoding="utf-8"))
for k in sorted(hist.keys()):
    v = hist[k]
    if isinstance(v, (int, float, str)) and len(str(v)) < 60:
        print("history", k, "=", v)
