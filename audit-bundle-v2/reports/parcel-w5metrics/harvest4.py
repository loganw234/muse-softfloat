#!/usr/bin/env python3
"""Harvest 4: study bases/timeboxes, lead escalation answers, tokens method heads."""
import re
from pathlib import Path

WS = Path(r"C:\Users\logan\source\repos\Muse-Softfloat")


def lines_of(p):
    try:
        return p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


print("## study ledgers: base/timebox lines")
for stem in ("study-tier2-oracle0b", "study-tier2-trigspike", "study-sf2-algebraic",
             "study-sf2-attribute", "study-sf2-augmented", "study-sf2-explog",
             "study-kissfft-visual", "study-tokens-visual", "sf0-evidence-auditor",
             "auditor-adherence-2"):
    ls = lines_of(WS / "ledger" / f"{stem}.md")
    print(f"\n### {stem} ({len(ls)} lines)")
    for ln in ls[:6]:
        print(f"  {ln.strip()[:170]}")
    for i, ln in enumerate(ls, 1):
        if re.search(r"\bbase\b|time box|HEAD|main @|cut from", ln, re.I) and i > 6:
            print(f"  L{i}: {ln.strip()[:170]}")
            break

print("\n## lead.md headings + escalation mentions")
lead = lines_of(WS / "ledger/lead.md")
print(f"lead.md lines={len(lead)}")
heads = [(i, ln.strip()) for i, ln in enumerate(lead, 1) if ln.startswith("## ")]
print(f"headings={len(heads)}")
for i, h in heads:
    if "2026-10-27 1" in h or "2026-10-28" in h or "2026-10-29" in h:
        print(f"  L{i}: {h[:170]}")
print("\n-- escalation-word lines in lead.md --")
for i, ln in enumerate(lead, 1):
    if re.search(r"escalat", ln, re.I):
        print(f"  L{i}: {ln.strip()[:200]}")

print("\n## tokens study: files + method heads")
d = WS / "scratch/study-tokens-visual"
for p in sorted(d.rglob("*")):
    if p.is_file() and "cft" not in p.name.lower():
        print(f"  {p.relative_to(d)} {p.stat().st_size}")
for name in ("report.md",):
    ls = lines_of(d / name)
    print(f"--- {name} first 40 ---")
    for ln in ls[:40]:
        print(f"  {ln.strip()[:190]}")
