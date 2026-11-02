#!/usr/bin/env python3
"""Summarize inventory1.json: work sessions vs frozen rows, label quality."""
import json
from pathlib import Path

HERE = Path(__file__).parent
WS = HERE.parents[1]
inv = json.loads((HERE / "inventory1.json").read_text(encoding="utf-8"))

frozen_sessions = {}
for name in ("usage", "passes"):
    for line in (WS / "worktrees/w5-metrics/docs/metrics" / f"{name}.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        note = row.get("note", "")
        for token in note.replace(";", " ").split():
            if len(token) == 36 and token.count("-") == 4:
                frozen_sessions[token] = row.get("agent")

rows = inv["lead_subtree"]
work = [r for r in rows if not r["internal_reminder"]]
work.sort(key=lambda r: r["start"] or "")
print(f"frozen session ids in notes: {len(frozen_sessions)}")
present = {r["session"] for r in rows}
missing = [s for s in frozen_sessions if s not in present]
print(f"frozen sessions absent from lead subtree: {len(missing)}")
for s in missing:
    print(f"  PRUNED? {s} agent={frozen_sessions[s]}")
print()
print(f"{'start':<26} {'end':<26} {'frozen?':<8} {'extractor-label':<24} evidence")
new = []
for r in work:
    tag = "FROZEN" if r["session"] in frozen_sessions else ""
    lab = r["role_label_extractor"] or "(id)"
    ev = ",".join(r["labels"][:4])
    print(f"{(r['start'] or '?'):<26} {(r['end'] or '?'):<26} {tag:<8} {lab:<24} {r['session'][:13]} {ev}")
    if not tag and not r["is_main"]:
        new.append(r)
print()
print(f"new work child sessions (excl main): {len(new)}")
tots = {"in": 0, "out": 0, "cached": 0, "msgs": 0}
for r in new:
    for m, u in r["usage_by_model"].items():
        tots["in"] += u.get("input_tokens", 0)
        tots["out"] += u.get("output_tokens", 0)
        tots["cached"] += u.get("cached_tokens", 0)
        tots["msgs"] += r["messages_by_model"].get(m, 0)
print(f"new-child totals (full files, no cutoff): in={tots['in']:,} out={tots['out']:,} cached={tots['cached']:,} msgs={tots['msgs']:,}")
main = next(r for r in rows if r["is_main"])
print(f"main span {main['start']} .. {main['end']} bytes={main['bytes']:,}")
for m, u in main["usage_by_model"].items():
    print(f"  main {m}: in={u.get('input_tokens',0):,} out={u.get('output_tokens',0):,} cached={u.get('cached_tokens',0):,} msgs={main['messages_by_model'].get(m,0):,}")
print()
print("top-level mirrors not also subagent:")
for m in inv["top_mirrors"]:
    if not m["also_subagent"]:
        u = sum(v.get("input_tokens", 0) for v in m["usage_by_model"].values())
        print(f"  {m['rel']} bytes={m['bytes']:,} in={u:,} start={m['start']}")
print("mirrors that ARE subagents: byte comparison (mirror vs subagent):")
sub = {r["session"]: r for r in rows if not r["is_main"]}
for m in inv["top_mirrors"]:
    if m["also_subagent"]:
        s = sub[m["session"]]
        same = "SAME-SHA" if m["sha256_12"] == s["sha256_12"] else "DIFF"
        print(f"  {m['session'][:13]} mirror={m['bytes']:,} sub={s['bytes']:,} {same}")
