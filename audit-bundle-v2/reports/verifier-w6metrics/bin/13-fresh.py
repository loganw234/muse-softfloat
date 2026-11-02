#!/usr/bin/env python3
"""Probe 5b: sessions newer than the cutoff — role labels only, counts only.

Lists lead-store subagent sessions whose transcript was modified after the
parcel cutoff, with only the extractor's agent label (Role: / searched /
session id), to check whether any in-span agent lacks an appended row.
No prompt text is printed.
"""
import json
import os
import datetime

CUTOFF = "2026-10-30T16:08:00-07:00"
LEAD = ("C:/Users/logan/.local/share/muse/sessions/2026/10/26/"
        "01a17907-4147-7333-a565-56071da9d971/subagent")
OUT = os.environ["OUT"]

cutoff_ts = datetime.datetime.fromisoformat(CUTOFF).timestamp()
known = set()
for line in open(os.path.join(OUT, "app-usage.jsonl"), encoding="utf-8"):
    import re
    for s in re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
                        r"[0-9a-f]{4}-[0-9a-f]{12}", json.loads(line)["note"]):
        known.add(s)

import sys
sys.path.insert(0, os.path.join(os.environ["DUP"], "tools"))
import extract_session_metrics as E

fresh = []
for d in sorted(os.listdir(LEAD)):
    p = os.path.join(LEAD, d, "session.jsonl")
    if not os.path.isfile(p):
        continue
    if os.path.getmtime(p) <= cutoff_ts:
        continue
    fresh.append(d)

print(f"subagent transcripts modified after cutoff: {len(fresh)}")
for d in fresh:
    p = os.path.join(LEAD, d, "session.jsonl")
    try:
        st = E.extract_session(E.Path(p), False, "wave?", E.parse_until(CUTOFF))
    except Exception as e:
        print(f"{d}: extractor refused ({e})")
        continue
    if st is None:
        print(f"POST-CUTOFF {d} (no records at or before cutoff)")
        continue
    tag = "ROWED" if d in known else "UNROWED"
    # label only (role-label carve-out); end time at cutoff shows span
    print(f"{tag} {d} label={st['agent']} end-at-cutoff={E.iso_local(st['end'])}")
