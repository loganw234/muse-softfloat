#!/usr/bin/env python3
"""Deep role-label probe for two ambiguous sessions. Prints labels only."""
import json
import re
import sys
from pathlib import Path

STORE = Path(r"C:\Users\logan\.local\share\muse\sessions\2026\10\26\01a17907-4147-7333-a565-56071da9d971\subagent")
PATS = [
    ("youare", re.compile(r"You are ([a-z][a-z0-9]+(?:-[a-z0-9]+)+)")),
    ("role", re.compile(r"Role:\s*\**\s*([A-Za-z0-9][A-Za-z0-9_-]*)")),
    ("brief", re.compile(r"ledger/briefs/([A-Za-z0-9_.-]+\.md)")),
    ("scratch", re.compile(r"scratch/([a-z0-9][a-z0-9_-]*)/")),
    ("worktree", re.compile(r"worktrees/([a-z0-9][a-z0-9_-]*)/")),
    ("ledgerfile", re.compile(r"ledger/([a-z0-9][a-z0-9_-]*\.md)")),
    ("fixword", re.compile(r"\b(fixer|rechecker|fix child|fix pass)\b", re.I)),
]


def strings(obj, out, limit=60):
    if len(out) >= limit:
        return
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            strings(v, out, limit)
    elif isinstance(obj, list):
        for v in obj:
            strings(v, out, limit)


for sid in sys.argv[1:]:
    path = STORE / sid / "session.jsonl"
    print(f"===== {sid} =====")
    seen = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for n, line in enumerate(f, 1):
            if n > 400:
                break
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            strs = []
            strings(rec, strs)
            for s in strs:
                for tag, pat in PATS:
                    m = pat.search(s)
                    if m:
                        hit = f"rec{n} {tag}:{m.group(1)}"
                        if hit not in seen:
                            seen.append(hit)
    for h in seen[:30]:
        print(f"  {h}")
