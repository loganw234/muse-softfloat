#!/usr/bin/env python3
"""Probe 5c: role labels + start times of the 5 post-cutoff sessions.

Label-only output (role-label carve-out): agent label, internal flag,
start/end. No prompt text, no counts.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.environ["DUP"], "tools"))
import extract_session_metrics as E

LEAD = ("C:/Users/logan/.local/share/muse/sessions/2026/10/26/"
        "01a17907-4147-7333-a565-56071da9d971/subagent")
fresh = ["6652579b-19e8-7bbb-8ecc-ba71c89b58b3",
         "6652589b-19e8-7d6e-8ecc-bb71c89b5a66",
         "833d2036-cf3f-7834-81f5-34108aececcc",
         "833d2336-cf3f-7d4d-81f5-37108aecf1e5",
         "f469368e-eca3-773a-8a11-e68308d3f932"]
for d in fresh:
    p = os.path.join(LEAD, d, "session.jsonl")
    try:
        st = E.extract_session(E.Path(p), False, "wave?", None)
    except Exception as e:
        print(f"{d}: refused ({e})")
        continue
    print(f"{d} label={st['agent']} how={st['how']} internal={st['internal']} "
          f"start={E.iso_local(st['start'])}")
