"""counters2.py - predicted post-fix sampler output + metrics line counts.
Read-only. Simulates site/build_data.py with the pair_call fix and the
exact-shape guard (len(tok) == arrow+4), without touching site/.
"""
import collections
import json
import re
from pathlib import Path

WS = Path(__file__).resolve().parents[2]
WT = WS / "worktrees" / "w5-readme3"

text = (WT / "tests" / "msf_dispatch.h").read_text(encoding="utf-8", errors="replace")
i = text.find("static const msf_op_desc_t MSF_OPS[]")
j = text.find("};", i)
pat = re.compile(
    r'\{\s*"([^"]+)",\s*"([^"]+)",\s*(MSF_SIG_\w+),\s*(MSF_RK_\w+),'
    r'\s*\{\s*(MSF_AK_\w+),\s*(MSF_AK_\w+),\s*(MSF_AK_\w+)\s*\},'
    r'\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\w+),\s*(\w+)\s*\}')
ops = []
for m in pat.finditer(text[i:j]):
    ops.append({"name": m.group(1), "nargs": int(m.group(8)),
                "runnable": m.group(13) != "0", "pair": m.group(14) != "0"})
runnable = {o["name"]: o for o in ops if o["runnable"]}
print(f"ops={len(ops)} runnable={len(runnable)} pair={sum(o['pair'] for o in ops)}")

by_op = collections.defaultdict(list)
skipped_shape = 0
for p in sorted((WT / "tests" / "vectors").glob("*.vec")):
    for raw in p.read_text(encoding="utf-8", errors="replace").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        tok = s.split()
        if tok[0] not in runnable or "~" in tok or "->" not in tok:
            continue
        arrow = tok.index("->")
        op = runnable[tok[0]]
        args = tok[2:arrow]
        if len(args) != op["nargs"] or len(tok) != arrow + 4:
            skipped_shape += 1
            continue
        by_op[tok[0]].append(tok)
print("skipped by exact-shape guard (runnable ops only):", skipped_shape)
sample = []
for name in sorted(by_op):
    lines = by_op[name]
    for pick in sorted({0, len(lines) // 2}):
        sample.append(lines[pick])
covered = {s[0] for s in sample}
print(f"predicted sample={len(sample)} ops_covered={len(covered)}")
print("runnable ops with no sampled line:", sorted(set(runnable) - covered))
print("explog in sample:", sum(1 for s in sample if "exp2" in s[0] or "log2" in s[0]))
print("aug in sample:", sum(1 for s in sample if "augmented" in s[0]))
print("ops with exactly one committed line bucket:",
      sum(1 for v in by_op.values() if len(v) == 1))

print("\nmetrics jsonl line counts:")
for f in ["usage.jsonl", "passes.jsonl", "briefs.jsonl", "corrections.jsonl",
          "escalations.jsonl", "plants.jsonl", "fetches.jsonl"]:
    p = WT / "docs" / "metrics" / f
    lines = [x for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
    for x in lines:
        json.loads(x)
    print(f"{f}: {len(lines)} rows (all parse)")
print("COUNTERS2 DONE")
