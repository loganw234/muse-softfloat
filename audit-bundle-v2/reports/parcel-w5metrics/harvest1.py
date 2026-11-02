#!/usr/bin/env python3
"""Harvest annotation evidence: verifier verdicts/classes, urgent files, briefs diff.

Prints bounded excerpts (verdict lines, finding-tag lines, file heads) with
paths so every annotation can cite a source. No session logs read here.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

WS = Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
WT = WS / "worktrees/w5-metrics"


def iso(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone().isoformat(timespec="seconds")


def lines_of(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


print("## verifier ledgers + reports: verdict + finding tags")
VERD = re.compile(r"NOT READY|(?<!NOT )READY|\bPASS\b|verdict", re.I)
FTAG = re.compile(r"^\s*[-*]?\s*F[- ]?\w*\s*\((a|b|a/b|b/a)\)", re.I)
CLASSDEF = re.compile(r"class a|\(a\)\s*=|a = regression", re.I)
agents = sorted({p.stem for p in (WS / "ledger").glob("verifier-*.md")} |
                {p.stem for p in (WS / "ledger").glob("rechecker*.md")})
for stem in agents:
    lp = WS / "ledger" / f"{stem}.md"
    rp = WS / "scratch" / stem / "report.md"
    print(f"\n### {stem}")
    for label, path in (("ledger", lp), ("report", rp)):
        ls = lines_of(path)
        if not ls:
            print(f"  {label}: MISSING {path}")
            continue
        hits = []
        for i, ln in enumerate(ls[:400], 1):
            if CLASSDEF.search(ln) or FTAG.search(ln):
                hits.append(f"L{i}: {ln.strip()[:150]}")
            elif i <= 6 and VERD.search(ln):
                hits.append(f"L{i}: {ln.strip()[:150]}")
        print(f"  {label} {path.name} ({len(ls)} lines):")
        for h in hits[:14]:
            print(f"    {h}")
        if not hits:
            print(f"    head: {ls[0].strip()[:150] if ls else ''}")

print("\n## ledger/urgent files (escalation candidates)")
for p in sorted((WS / "ledger/urgent").glob("*.md")):
    ls = lines_of(p)
    print(f"- {p.name} mtime={iso(p.stat().st_mtime)} bytes={p.stat().st_size}")
    for ln in ls[:4]:
        print(f"    {ln.strip()[:160]}")

print("\n## briefs: ledger/briefs vs briefs.jsonl authors")
brief_rows = [json.loads(x) for x in (WT / "docs/metrics/briefs.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
have = {r["author"] for r in brief_rows}
print(f"briefs.jsonl authors ({len(have)}): {sorted(have)}")
for p in sorted((WS / "ledger/briefs").glob("*.md")):
    ls = lines_of(p)
    head = " ".join(x.strip() for x in ls[:3])[:170]
    tb = ""
    for ln in ls:
        m = re.search(r"[Tt]ime box\D{0,12}?(\d+)\s*min", ln)
        if m:
            tb = m.group(1)
            break
    base = ""
    for ln in ls[:12]:
        m = re.search(r"\b([0-9a-f]{40}|[0-9a-f]{7})\b", ln)
        if m and ("base" in ln.lower() or "cut" in ln.lower() or "main" in ln.lower()):
            base = m.group(1)
            break
    print(f"- {p.name} timebox={tb or '?'} base={base or '?'} :: {head}")
