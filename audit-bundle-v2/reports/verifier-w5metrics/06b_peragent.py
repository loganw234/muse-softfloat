#!/usr/bin/env python3
"""Probe 6B: per-agent recount from sessions named in row notes vs rows."""
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

WS = Path("C:/Users/logan/source/repos/Muse-Softfloat")
COPY = WS / "worktrees/verify5-metrics"
STORE = Path("C:/Users/logan/.local/share/muse/sessions/2026/10/26/01a17907-4147-7333-a565-56071da9d971/subagent")
CUTOFF = "2026-10-29T11:39:55-07:00"

sys.path.insert(0, str(WS / COPY / "tools"))
import extract_session_metrics as E  # noqa: E402

out = subprocess.run(["git", "-C", str(COPY), "show", "HEAD:docs/metrics/usage.jsonl"],
                     capture_output=True, check=True, text=True).stdout.splitlines()
rows = [json.loads(l) for l in out]
until_micros = E.parse_until(CUTOFF)
cache = {}
fails = 0
for r in rows:
    sess = list(dict.fromkeys(
        re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", r["note"])))
    agg = defaultdict(int)
    for s in sess:
        if s not in cache:
            p = STORE / s / "session.jsonl"
            if s == "01a17907-4147-7333-a565-56071da9d971":
                p = STORE.parent / "session.jsonl"
            r_ = E.extract_session(p, s.startswith("01a17907"), "waveX", until_micros) if p.is_file() else None
            cache[s] = r_
        r_ = cache[s]
        if r_ is None:
            print(f"{r['agent']}: session {s} returns None")
            continue
        for m, u in r_["usage_by_model"].items():
            agg[(m, "o")] += u["output_tokens"]
            agg[(m, "i")] += u["input_tokens"]
            agg[(m, "c")] += u["cached_tokens"]
        for m, v in r_["messages_by_model"].items():
            agg[(m, "m")] += v
    got = (agg.get((r["model"], "o"), 0), agg.get((r["model"], "i"), 0),
           agg.get((r["model"], "c"), 0), agg.get((r["model"], "m"), 0))
    exp = (r["output_tokens"], r["input_tokens"], r.get("cached_tokens", 0), r["messages"])
    if got != exp:
        fails += 1
        print(f"{r['wave']} {r['agent']} {r['model']}: row={exp} recomputed={got} "
              f"dout={got[0]-exp[0]} din={got[1]-exp[1]} dmsgs={got[3]-exp[3]}")
print("agents checked:", len(rows), "mismatched:", fails)
