#!/usr/bin/env python3
"""Reconcile appended metrics vs scratch/study-tokens-visual/data/tokens.json.

Streams the lead subtree twice (their tmax, my SF-2-close cutoff) with the
shared counting rules (model_completed usage, exact-duplicate suppression),
split by main / internal-reminder / frozen-child / new-child, then ties the
pieces to tokens.json and to the extractor + fold totals. Numbers only.
"""
import collections
import json
import re
from datetime import datetime
from pathlib import Path

WS = Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
HERE = Path(__file__).parent
LEAD = Path(r"C:\Users\logan\.local\share\muse\sessions\2026\10\26\01a17907-4147-7333-a565-56071da9d971")
FIELDS = ("input_tokens", "output_tokens", "cached_tokens",
          "cache_write_tokens", "cache_read_tokens", "reasoning_tokens")
TOK = json.loads((WS / "scratch/study-tokens-visual/data/tokens.json").read_text(encoding="utf-8"))
TREEU = json.loads((WS / "scratch/study-tokens-visual/tree_usage.json").read_text(encoding="utf-8"))
T_TOK = TREEU["tmax"]
T_MY = round(datetime.fromisoformat("2026-10-29T11:39:55-07:00").timestamp() * 1_000_000)

inv = json.loads((HERE / "inventory1.json").read_text(encoding="utf-8"))
internal_sids = {r["session"] for r in inv["lead_subtree"] if r["internal_reminder"]}
SID = re.compile(r"session ([0-9a-f-]{36})")
def load(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
frozen_rows = load(WS / "worktrees/w5-metrics/docs/metrics/usage.jsonl")
frozen_sids = {SID.search(r["note"]).group(1) for r in frozen_rows}
LEAD_SID = LEAD.name


def scan(path, until):
    usage = collections.Counter()
    msgs = 0
    seen = set()
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            try:
                d = json.loads(s)
            except json.JSONDecodeError:
                continue
            ts = d.get("recorded_at")
            if isinstance(ts, int) and ts > until:
                continue
            pay = d.get("payload")
            if not isinstance(pay, dict):
                continue
            ev = pay.get("event")
            if not isinstance(ev, dict) or ev.get("kind") != "model_completed":
                continue
            u, model = ev.get("usage"), ev.get("model")
            if not isinstance(u, dict) or not isinstance(model, str):
                continue
            key = (ts, model, ev.get("duration_ms")) + tuple(u.get(f) for f in FIELDS)
            if key in seen:
                continue
            seen.add(key)
            for f in FIELDS:
                v = u.get(f, 0)
                if isinstance(v, int) and v >= 0:
                    usage[f] += v
            msgs += 1
    return usage, msgs


files = [(LEAD / "session.jsonl", LEAD_SID)]
files += [(p, p.parent.name) for p in sorted((LEAD / "subagent").glob("*/session.jsonl"))]

def bucket(sid):
    if sid == LEAD_SID:
        return "main"
    if sid in internal_sids:
        return "internal"
    if sid in frozen_sids:
        return "frozen_child"
    return "new_child"

results = {}
per_session_delta = []
for label, until in (("tokens_tmax", T_TOK), ("my_cutoff", T_MY)):
    tot = collections.defaultdict(lambda: (collections.Counter(), 0))
    store = {}
    for path, sid in files:
        u, m = scan(path, until)
        store[sid] = (u, m)
        b = bucket(sid)
        c, mm = tot[b]
        c.update(u)
        tot[b] = (c, mm + m)
    results[label] = (tot, store)
    allc = collections.Counter()
    allm = 0
    for c, mm in tot.values():
        allc.update(c)
        allm += mm
    print(f"[{label} until={until}] files={len(files)} msgs={allm:,} in={allc['input_tokens']:,} "
          f"out={allc['output_tokens']:,} cached={allc['cached_tokens']:,}")
    for b in ("main", "internal", "frozen_child", "new_child"):
        c, mm = tot[b]
        print(f"  {b:<13} msgs={mm:>6,} in={c['input_tokens']:>13,} out={c['output_tokens']:>10,} cached={c['cached_tokens']:>13,}")

print("\n[tokens.json tree] msgs=%s in=%s out=%s cached=%s files=%s" % (
    f"{TOK['tree']['msgs']:,}", f"{TOK['tree']['in']:,}", f"{TOK['tree']['out']:,}",
    f"{TOK['tree']['cached']:,}", TOK["tree"]["files"]))
tok_tot, _ = results["tokens_tmax"]
mine_all = collections.Counter()
for c, _ in tok_tot.values():
    mine_all.update(c)
for f, k in (("input_tokens", "in"), ("output_tokens", "out"), ("cached_tokens", "cached")):
    print(f"  tree-compare {k}: mine={mine_all[f]:,} theirs={TOK['tree'][k]:,} diff={mine_all[f]-TOK['tree'][k]:,}")

print("\n[span bridge: new_child growth tokens_tmax -> my_cutoff, per session]")
_, s_tok = results["tokens_tmax"]
_, s_my = results["my_cutoff"]
for path, sid in files:
    if bucket(sid) != "new_child":
        continue
    (u1, m1), (u2, m2) = s_tok[sid], s_my[sid]
    d_in = u2["input_tokens"] - u1["input_tokens"]
    d_out = u2["output_tokens"] - u1["output_tokens"]
    if d_in or d_out or m2 != m1:
        per_session_delta.append(sid)
        print(f"  {sid} dmsgs={m2-m1} din={d_in:,} dout={d_out:,}")

new_rows = load(HERE / "new-usage.jsonl")
nr = {f: sum(r[f] for r in new_rows) for f in ("input_tokens", "output_tokens", "cached_tokens", "messages")}
my_tot, _ = results["my_cutoff"]
nc, nm = my_tot["new_child"]
print(f"\n[fold tie] new rows: in={nr['input_tokens']:,} out={nr['output_tokens']:,} cached={nr['cached_tokens']:,} msgs={nr['messages']:,}")
print(f"[fold tie] streamed new_child @cutoff: in={nc['input_tokens']:,} out={nc['output_tokens']:,} cached={nc['cached_tokens']:,} msgs={nm:,}")
fz = {f: sum(r[f] for r in frozen_rows) for f in ("input_tokens", "output_tokens", "cached_tokens", "messages")}
print(f"[frozen usage file totals] in={fz['input_tokens']:,} out={fz['output_tokens']:,} cached={fz['cached_tokens']:,} msgs={fz['messages']:,}")
fc, fm = my_tot["frozen_child"]
print(f"[streamed frozen_child @cutoff] in={fc['input_tokens']:,} out={fc['output_tokens']:,} cached={fc['cached_tokens']:,} msgs={fm:,} "
      f"(frozen file minus lead row: in={fz['input_tokens']-29136439:,} out={fz['output_tokens']-116106:,})")
mc, mm2 = my_tot["main"]
print(f"[lead main @cutoff] in={mc['input_tokens']:,} out={mc['output_tokens']:,} msgs={mm2:,}; frozen lead row in=29,136,439 out=116,106 msgs=132 "
      f"-> unrowed lead after wave0 cut: in={mc['input_tokens']-29136439:,} out={mc['output_tokens']-116106:,} msgs={mm2-132:,}")
ic, im = my_tot["internal"]
print(f"[internal reminders @cutoff] in={ic['input_tokens']:,} out={ic['output_tokens']:,} msgs={im:,} files={len(internal_sids)}")
print(f"\n[tokens grand check] their grand in={TOK['grand']['in']:,} = tree {TOK['tree']['in']:,} + missing {TOK['missing_sessions']['in']:,}; "
      f"the 3 sessions are inside tree (frozen_child bucket), so grand double-counts {TOK['missing_sessions']['in']:,} in / "
      f"{TOK['missing_sessions']['out']:,} out / {TOK['missing_sessions']['msgs']} msgs; corrected billed = tree in+out = {TOK['tree']['in']+TOK['tree']['out']:,}")
