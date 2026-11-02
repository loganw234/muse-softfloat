import json
from pathlib import Path

p = Path("muse-softfloat/docs/metrics/usage.jsonl")
rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
print("rows", len(rows))
print("keys", sorted(rows[0].keys()))
for r in rows[:2]:
    print(r)
tot = {}
waves = {}
for r in rows:
    for k in ("input_tokens", "output_tokens", "cached_tokens", "messages", "in", "out", "cached", "msgs"):
        if k in r and isinstance(r[k], (int, float)):
            tot[k] = tot.get(k, 0) + r[k]
    w = r.get("wave", "?")
    waves[w] = waves.get(w, 0) + 1
print("totals", tot)
print("waves", waves)
billed = tot.get("input_tokens", tot.get("in", 0)) + tot.get("output_tokens", tot.get("out", 0))
print("billed", billed)
owner = 1928
print("ratio 1 in", round(billed / owner))
print("human share pct", owner / billed * 100)
