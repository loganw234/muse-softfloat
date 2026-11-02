#!/usr/bin/env python3
"""Probe 6: independent recount over the lead subtree at the parcel cutoff
(and at the study tmax); fold totals vs recount; study bridge; double-count.
Uses the copy's sanctioned counter read-only, file by file (streamed log:
one file at a time, no bulk load). Never modifies the copy."""
import json
import subprocess
import sys
from pathlib import Path

WS = Path("C:/Users/logan/source/repos/Muse-Softfloat")
COPY = Path("worktrees/verify5-metrics")
STORE = Path("C:/Users/logan/.local/share/muse/sessions/2026/10/26/01a17907-4147-7333-a565-56071da9d971")
CUTOFF = "2026-10-29T11:39:55-07:00"
TMAX = "2026-10-28T20:07:54-07:00"

sys.path.insert(0, str(WS / COPY / "tools"))
import extract_session_metrics as E  # noqa: E402


def git_show_rows(name, skip):
    out = subprocess.run(["git", "-C", str(WS / COPY), "show", f"HEAD:docs/metrics/{name}"],
                         capture_output=True, check=True, text=True).stdout.splitlines()
    return [json.loads(l) for l in out[skip:]]


def recount(until_s):
    until_micros = E.parse_until(until_s)
    main = STORE / "session.jsonl"
    files = [(main, True)] + [(p, False) for p in sorted((STORE / "subagent").glob("*/session.jsonl"))]
    work, internal = [], []
    for p, is_main in files:
        try:
            s = E.extract_session(p, is_main, "waveX", until_micros)
        except Exception as e:  # noqa: BLE001 -- report, don't stop
            print(f"REFUSED {p.parent.name if not is_main else 'MAIN'}: {e}")
            continue
        if s is None:
            continue
        (work if not s["internal"] else internal).append(s)
    return work, internal


def totals(sessions):
    o = i = c = m = 0
    for s in sessions:
        for u in s["usage_by_model"].values():
            o += u["output_tokens"]; i += u["input_tokens"]; c += u["cached_tokens"]
        for v in s["messages_by_model"].values():
            m += v
    return o, i, c, m


def row_totals(rows):
    return (sum(r["output_tokens"] for r in rows), sum(r["input_tokens"] for r in rows),
            sum(r.get("cached_tokens", 0) for r in rows), sum(r.get("messages", 0) for r in rows))


print("=== recount at parcel cutoff", CUTOFF)
work, internal = recount(CUTOFF)
print(f"sessions: {len(work)} work, {len(internal)} internal")
o, i, c, m = totals(work)
print(f"recount totals: out={o} in={i} cached={c} msgs={m}")

frozen_u = git_show_rows("usage.jsonl", 0)[:39]
appended_u = git_show_rows("usage.jsonl", 39)
fo, fi, fc, fm = row_totals(frozen_u)
ao, ai, ac, am = row_totals(appended_u)
print(f"frozen rows:  out={fo} in={fi} cached={fc} msgs={fm}")
print(f"appended rows: out={ao} in={ai} cached={ac} msgs={am}")
print(f"fold rows sum: out={fo+ao} in={fi+ai} cached={fc+ac} msgs={fm+am}")
print(f"recount-fold delta: out={o-(fo+ao)} in={i-(fi+ai)} cached={c-(fc+ac)} msgs={m-(fm+am)}")

# frozen child-session re-derivation (38 frozen children; lead row is cut, skip it)
print("=== frozen children re-derivation (38)")
frozen_by_session = {}
for r in frozen_u:
    if r["agent"] == "lead":
        continue
    import re
    ms = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", r["note"])
    for s in ms:
        frozen_by_session[s] = r
exact = mismatch = 0
for sess, r in sorted(frozen_by_session.items()):
    s = next((w for w in work if w["session"] == sess), None)
    if s is None:
        print(f"  {r['agent']}: session file absent from recount (pruned?) MISMATCH"); mismatch += 1; continue
    ro = sum(u["output_tokens"] for u in s["usage_by_model"].values())
    ri = sum(u["input_tokens"] for u in s["usage_by_model"].values())
    rc = sum(u["cached_tokens"] for u in s["usage_by_model"].values())
    rm = sum(s["messages_by_model"].values())
    ok = (ro, ri, rc, rm) == (r["output_tokens"], r["input_tokens"], r.get("cached_tokens", 0), r["messages"])
    if ok:
        exact += 1
    else:
        mismatch += 1
        print(f"  {r['agent']}: row=({r['output_tokens']},{r['input_tokens']},{r.get('cached_tokens',0)},{r['messages']}) "
              f"rec=({ro},{ri},{rc},{rm}) MISMATCH")
print(f"frozen children: {exact} exact, {mismatch} mismatch (of {len(frozen_by_session)} sessions)")

print("=== recount at study tmax", TMAX)
work_t, internal_t = recount(TMAX)
ot, it, ct, mt = totals(work_t)
print(f"tmax sessions: {len(work_t)} work, {len(internal_t)} internal")
print(f"tmax totals: out={ot} in={it} cached={ct} msgs={mt}")
print("study tree:  out=6444124 in=1469302586 cached=1424594514 msgs=8709")
print(f"tmax-tree delta: out={ot-6444124} in={it-1469302586} cached={ct-1424594514} msgs={mt-8709}")
