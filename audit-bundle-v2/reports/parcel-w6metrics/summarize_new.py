#!/usr/bin/env python3
import json, re
from pathlib import Path
WS = Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
HERE = Path(__file__).parent
inv = json.loads((HERE / "inventory.json").read_text(encoding="utf-8"))["lead_subtree"]
def load(p): return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
SID = re.compile(r"session[s]? ([0-9a-f-]{36})")
frozen = set()
for r in load(WS / "worktrees/w6-metrics/docs/metrics/usage.jsonl"):
    for m in re.finditer(r"[0-9a-f]{8}-[0-9a-f-]{27,}", r.get("note","")):
        frozen.add(m.group(0))
print("frozen sids in usage notes:", len(frozen))
work = [r for r in inv if not r["internal_reminder"] and r["start"] is not None]
new = [r for r in work if r["session"] not in frozen and not r["is_main"]]
old = [r for r in work if r["session"] in frozen]
print(f"work at cutoff={len(work)} old={len(old)} new={len(new)} main_in_new={any(r['is_main'] for r in new)}")
missing = frozen - {r["session"] for r in inv}
print("frozen sids not on disk:", sorted(missing))
new.sort(key=lambda r: r["start"])
tot_in = tot_out = tot_msg = 0
for r in new:
    i = sum(v.get("input_tokens",0) for v in r["usage_by_model"].values())
    o = sum(v.get("output_tokens",0) for v in r["usage_by_model"].values())
    m = sum(r["messages_by_model"].values())
    tot_in += i; tot_out += o; tot_msg += m
    models = ",".join(k.replace("muse-","") for k in r["usage_by_model"])
    print(f"{r['start']} .. {r['end']} {r['session'][:13]} role={r['role_label']} youare={r['youare']} hits={r['parcel_hits_head']} labels={r['labels'][:4]} models={models} in={i:,} out={o:,} msgs={m} tools={r['tool_uses']}")
print(f"NEW TOTALS in={tot_in:,} out={tot_out:,} msgs={tot_msg}")
# sessions with records after cutoff among new/old
for r in inv:
    if r["records_after_cutoff"] and not r["is_main"]:
        print("AFTER-CUTOFF records:", r["session"], r["records_after_cutoff"], "start", r["start"])
