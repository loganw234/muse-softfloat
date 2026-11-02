#!/usr/bin/env python3
"""Probe 4: independent extractor recount of appended agents (counts only).

Uses the duplicate's tools/extract_session_metrics.py header contract:
model_completed usage only, exact-dup suppression, distinct tool-call ids,
one message per model_completed, --until cutoff. Compares recount sums
against the committed usage.jsonl / passes.jsonl rows to the unit.
"""
import json
import os
import re
import sys

DUP = os.environ["DUP"]
OUT = os.environ["OUT"]
CUTOFF = "2026-10-30T16:08:00-07:00"
STORE = ("C:/Users/logan/.local/share/muse/sessions/2026/10/26/"
         "01a17907-4147-7333-a565-56071da9d971/subagent")

sys.path.insert(0, os.path.join(DUP, "tools"))
import extract_session_metrics as E

until_micros = E.parse_until(CUTOFF)

targets = ["verifier-w6popups", "fixer-w6popups", "parcel-w6popups",
           "parcel-w6filmretime", "verifier-w6filmretime",
           "surveyor-epidemiclicense", "parcel-w6ci", "verifier-w6ci",
           "verifier-polish1", "auditor-staleinfo-spark"]

usage_rows = [json.loads(l) for l in
              open(os.path.join(OUT, "app-usage.jsonl"), encoding="utf-8")]
pass_rows = [json.loads(l) for l in
             open(os.path.join(OUT, "app-passes.jsonl"), encoding="utf-8")]
usage_by_agent = {r["agent"]: r for r in usage_rows}

mismatch = 0
for agent in targets:
    row = usage_by_agent[agent]
    sessions = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
                          r"[0-9a-f]{4}-[0-9a-f]{12}", row["note"])
    assert sessions, f"no session ids in note for {agent}"
    agg_in = agg_out = agg_cached = agg_msgs = 0
    per_session = []
    for s in sessions:
        p = os.path.join(STORE, s, "session.jsonl")
        st = E.extract_session(E.Path(p), False, row["wave"], until_micros)
        # Documented labelling gap: unlabelled Workflow children fall back
        # to the session id; the committed rows record this fallback in
        # their notes ("label via session id (unlabelled)"), so the
        # session-id label is expected, not a disagreement.
        for model, u in st["usage_by_model"].items():
            if model != row["model"]:
                print(f"{agent}: UNEXPECTED model {model} in {s}")
                mismatch += 1
            agg_in += u["input_tokens"]
            agg_out += u["output_tokens"]
            agg_cached += u["cached_tokens"]
            agg_msgs += st["messages_by_model"][model]
        per_session.append((st["end"], st["tool_uses"], s, st["agent"]))
    prow = sorted([r for r in pass_rows if r["agent"] == agent],
                  key=lambda r: r["end"])
    per_session.sort()
    ptools = [r["tool_uses"] for r in prow]
    rtools = [t for _, t, _, _ in per_session]
    tools_ok = (ptools == rtools)
    ok = (agg_in == row["input_tokens"] and agg_out == row["output_tokens"]
          and agg_cached == row["cached_tokens"] and agg_msgs == row["messages"]
          and tools_ok)
    flag = "MATCH" if ok else "MISMATCH"
    if not ok:
        mismatch += 1
    print(f"{flag} {agent}: committed(in={row['input_tokens']},"
          f"out={row['output_tokens']},cached={row['cached_tokens']},"
          f"msgs={row['messages']}) recount(in={agg_in},out={agg_out},"
          f"cached={agg_cached},msgs={agg_msgs}) "
          f"passes_tools={ptools} recount_tools={rtools} "
          f"nsessions={len(sessions)} labels={[a for _, _, _, a in per_session]}")
print(f"agents recounted: {len(targets)}, mismatches: {mismatch}")
print(f"cutoff used: {CUTOFF}")
