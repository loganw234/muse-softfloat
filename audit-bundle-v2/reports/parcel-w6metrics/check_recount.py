#!/usr/bin/env python3
"""Recount checks: new extractor output vs w5 extract-out (frozen sessions)
and vs the streaming inventory (all sessions); frozen-row spot checks."""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
WS = Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
HERE = Path(__file__).parent
def load(p): return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
SID = re.compile(r"session ([0-9a-f-]{36})")
def by_sid(rows):
    out = {}
    for r in rows:
        m = SID.search(r.get("note", ""))
        if m: out.setdefault(m.group(1), []).append(r)
    return out

new_u = by_sid(load(HERE / "extract-out/usage.jsonl"))
new_p = by_sid(load(HERE / "extract-out/passes.jsonl"))
old_u = by_sid(load(WS / "scratch/parcel-w5metrics/extract-out/usage.jsonl"))
old_p = by_sid(load(WS / "scratch/parcel-w5metrics/extract-out/passes.jsonl"))
print(f"new extract sids={len(new_u)} old extract sids={len(old_u)}")
diff = 0
for sid, rows in old_u.items():
    if sid not in new_u:
        print("MISSING in new extract:", sid); diff += 1; continue
    for r_old in rows:
        cand = [r for r in new_u[sid] if r["model"] == r_old["model"]]
        if not cand:
            print("MODEL MISSING", sid, r_old["model"]); diff += 1; continue
        r_new = cand[0]
        for f in ("output_tokens", "input_tokens", "cached_tokens", "messages"):
            if r_new[f] != r_old[f]:
                print(f"DIFF {sid} {r_old['agent']} {f}: old={r_old[f]} new={r_new[f]}"); diff += 1
    po, pn = old_p[sid][0], new_p[sid][0]
    for f in ("start", "end", "tool_uses"):
        if po[f] != pn[f]:
            print(f"PASS DIFF {sid} {po['agent']} {f}: old={po[f]} new={pn[f]}"); diff += 1
print("old-vs-new diffs (lead expected):", diff)

# inventory cross-check for the 45 new sids
inv = {r["session"]: r for r in json.loads((HERE / "inventory.json").read_text(encoding="utf-8"))["lead_subtree"]}
frozen_sids = set(old_u)
new_sids = [s for s in new_u if s not in frozen_sids]
print("new sids in extract:", len(new_sids))
bad = 0
for sid in new_sids:
    r = inv[sid]
    ei = sum(x["input_tokens"] for x in new_u[sid]); eo = sum(x["output_tokens"] for x in new_u[sid])
    em = sum(x["messages"] for x in new_u[sid])
    ii = sum(v.get("input_tokens", 0) for v in r["usage_by_model"].values())
    io = sum(v.get("output_tokens", 0) for v in r["usage_by_model"].values())
    im = sum(r["messages_by_model"].values())
    if (ei, eo, em) != (ii, io, im) or new_p[sid][0]["tool_uses"] != r["tool_uses"] \
       or new_p[sid][0]["start"] != r["start"] or new_p[sid][0]["end"] != r["end"]:
        print("INV DIFF", sid, (ei, eo, em), (ii, io, im), new_p[sid][0]["tool_uses"], r["tool_uses"],
              new_p[sid][0]["start"], r["start"], new_p[sid][0]["end"], r["end"]); bad += 1
print("inventory diffs on new sids:", bad)

# lead + totals
lead_new = [r for rows in new_u.values() for r in rows if r["agent"] == "lead"]
frozen_u = load(WS / "worktrees/w6-metrics/docs/metrics/usage.jsonl")
lead_frozen = [r for r in frozen_u if r["agent"] == "lead"]
def tot(rows): return (sum(r["input_tokens"] for r in rows), sum(r["output_tokens"] for r in rows),
                        sum(r.get("cached_tokens", 0) for r in rows), sum(r.get("messages", 0) for r in rows))
print("lead at cutoff (extractor): in,out,cached,msgs =", tot(lead_new))
print("lead frozen row(s):", tot(lead_frozen))
print("frozen usage totals:", tot(frozen_u), "billed=", sum(tot(frozen_u)[:2]))
new_rows = [r for s in new_sids for r in new_u[s]]
print("45 new sessions totals:", tot(new_rows), "billed=", sum(tot(new_rows)[:2]))
internal = [r for r in inv.values() if r["internal_reminder"] and r["start"]]
ii = sum(sum(v.get("input_tokens",0) for v in r["usage_by_model"].values()) for r in internal)
io = sum(sum(v.get("output_tokens",0) for v in r["usage_by_model"].values()) for r in internal)
im = sum(sum(r["messages_by_model"].values()) for r in internal)
print(f"internal reminder sessions at cutoff: n={len(internal)} in={ii:,} out={io:,} msgs={im}")
