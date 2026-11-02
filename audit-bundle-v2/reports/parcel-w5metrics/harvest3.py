#!/usr/bin/env python3
"""Harvest 3: findings sections of unresolved verifier reports; zero-usage check."""
import json
import re
from pathlib import Path

WS = Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
HERE = Path(__file__).parent


def lines_of(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


vers = ["verifier-w4trig", "verifier-w4kissfft", "verifier-readme", "verifier-readme2",
        "verifier-sf2", "verifier-w5alg1", "verifier-w5exp2", "verifier-w5log2",
        "verifier-w5site", "verifier-w5demo", "verifier-w5twiddledoc", "verifier-w5aug"]
for v in vers:
    print(f"\n===== {v} =====")
    for label, path in (("report", WS / "scratch" / v / "report.md"),
                        ("ledger", WS / "ledger" / f"{v}.md")):
        ls = lines_of(path)
        if not ls:
            print(f"-- {label}: MISSING")
            continue
        print(f"-- {label} ({len(ls)} lines) first 3:")
        for ln in ls[:3]:
            print(f"   {ln.strip()[:160]}")
        # findings-ish lines anywhere: numbered findings, F-tags, class tags, counts
        pats = re.compile(r"(finding|\(a\)|\(b\)|\(a/b\)|wrong.answer|regression|claim)", re.I)
        shown = 0
        for i, ln in enumerate(ls, 1):
            if shown >= 16:
                break
            s = ln.strip()
            if not s or len(s) > 260:
                continue
            if pats.search(s) and (s.startswith(("-", "*", "|", "#")) or re.match(r"F-?\d", s) or "finding" in s.lower()):
                print(f"   L{i}: {s[:190]}")
                shown += 1

print("\n===== work sessions with zero usage or zero messages =====")
inv = json.loads((HERE / "inventory1.json").read_text(encoding="utf-8"))
for r in inv["lead_subtree"]:
    if r["internal_reminder"]:
        continue
    if not r["usage_by_model"] or sum(r["messages_by_model"].values()) == 0:
        print(f"  ZERO {r['session']} main={r['is_main']} bytes={r['bytes']} start={r['start']}")
print("done")
