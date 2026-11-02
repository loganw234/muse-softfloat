#!/usr/bin/env python3
"""Print ledger + scratch report heads for candidate new agents (records only)."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
WS = Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
agents = """parcel-w5metrics verifier-w5metrics parcel-w5readme3 verifier-w5readme3
auditor-adherence-final parcel-polish1 verifier-polish1 study-w6sanitize
parcel-w6augint verifier-w6augint parcel-w6ci verifier-w6ci parcel-w6examples
verifier-w6examples parcel-w6sanitize verifier-w6sanitize parcel-w6judgemap
verifier-w6judgemap parcel-w6filmretime verifier-w6filmretime parcel-w6popups
verifier-w6popups study-epidemic-license""".split()
for a in agents:
    for p in (WS/"ledger"/f"{a}.md", WS/"scratch"/a/"report.md"):
        if p.exists():
            txt = p.read_text(encoding="utf-8", errors="replace").splitlines()
            print(f"\n===== {p.relative_to(WS)} ({len(txt)} lines) =====")
            for line in txt[:25]:
                print(line[:220])
        else:
            print(f"\n===== MISSING {p.relative_to(WS)} =====")
