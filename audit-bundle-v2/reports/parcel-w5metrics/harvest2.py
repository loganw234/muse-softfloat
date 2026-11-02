#!/usr/bin/env python3
"""Harvest 2: plants per verifier, finding classes, ambiguous sessions, escalations."""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

WS = Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
WT = WS / "worktrees/w5-metrics"
HERE = Path(__file__).parent


def lines_of(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


print("## plants.jsonl per verifier")
plants = [json.loads(x) for x in (WT / "docs/metrics/plants.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
byv = defaultdict(Counter)
for r in plants:
    byv[r["verifier"]][r["grade"]] += 1
for v in sorted(byv):
    print(f"  {v}: {dict(byv[v])}")

print("\n## verifier finding classes (report + ledger + brief class def)")
vers = ["verifier-w4seam", "verifier-w4minmax", "verifier-w4interval", "verifier-w4trig",
        "verifier-w4kissfft", "verifier-sf1", "verifier-readme", "verifier-readme2", "verifier-sf2",
        "verifier-w5attr", "verifier-w5alg1", "verifier-w5alg2", "verifier-w5exp2", "verifier-w5log2",
        "verifier-w5aug", "verifier-w5site", "verifier-w5demo", "verifier-w5twiddledoc",
        "verifier-extractor", "sf0-evidence-auditor"]
FIND = re.compile(r"(F-?\d+|Finding\s*\d+|^\s*\d+\.\s)", re.I)
TAG = re.compile(r"\((a/b|b/a|a|b)\)")
for v in vers:
    print(f"\n### {v}")
    # brief class definition
    for bp in sorted((WS / "ledger/briefs").glob("verify-*.md")) + [WS / "ledger/briefs/sf1-verify.md"]:
        ls = lines_of(bp)
        role = " ".join(ls[:2])
        if v in role or bp.stem.replace("verify-", "verifier-") == v:
            for ln in ls[:14]:
                if "Finding" in ln or "(a)" in ln:
                    print(f"  brief {bp.name}: {ln.strip()[:170]}")
                    break
    for label, path in (("ledger", WS / "ledger" / f"{v}.md"),
                        ("report", WS / "scratch" / v / "report.md")):
        ls = lines_of(path)
        if not ls:
            print(f"  {label}: MISSING")
            continue
        shown = 0
        for i, ln in enumerate(ls, 1):
            t = TAG.search(ln)
            if t and (FIND.search(ln) or "finding" in ln.lower() or ln.strip().startswith(("-", "*"))):
                print(f"  {label} L{i} [{t.group(1)}]: {ln.strip()[:150]}")
                shown += 1
            if shown >= 10:
                break
        if shown == 0:
            print(f"  {label}: no tagged finding lines in {len(ls)} lines; head: {ls[0].strip()[:120]}")

print("\n## ambiguous sessions detail")
inv = json.loads((HERE / "inventory1.json").read_text(encoding="utf-8"))
want = {"d322adf0", "d322acf0", "d34d7516", "d34d7816", "24110025", "18d430fa",
        "921371d5", "90de2274", "700f06e4", "49570560"}
for r in inv["lead_subtree"]:
    if r["session"][:8] in want:
        u = r["usage_by_model"]
        tot = {k: sum(v.get(k, 0) for v in u.values()) for k in ("input_tokens", "output_tokens")}
        print(f"  {r['session']} {r['start']}..{r['end']} youare={r['youare']} role_ex={r['role_label_extractor']} "
              f"role_relaxed={r['role_label_relaxed']} models={list(u)} msgs={sum(r['messages_by_model'].values())} "
              f"tools={r['tool_uses']} in={tot['input_tokens']:,} out={tot['output_tokens']:,} labels={r['labels']}")

print("\n## escalation mentions in parcel/study ledgers (wave4/5)")
ESC = re.compile(r"escalat", re.I)
for p in sorted((WS / "ledger").glob("*.md")):
    if p.name in ("lead.md", "README.md"):
        continue
    hits = [(i, ln.strip()[:170]) for i, ln in enumerate(lines_of(p), 1) if ESC.search(ln)]
    if hits:
        print(f"\n### {p.name}")
        for i, ln in hits[:8]:
            print(f"  L{i}: {ln}")

print("\n## missing-brief rows: timebox/base/ceiling lines")
for name in ("w4-trigspike", "sf2-algebraic", "sf2-attribute", "sf2-augmented", "sf2-explog",
             "study-kissfft-visual", "study-tokens-visual", "w5-exp2", "w5-metrics", "audit-adherence-2"):
    p = WS / "ledger/briefs" / f"{name}.md"
    print(f"\n### {name}")
    for i, ln in enumerate(lines_of(p), 1):
        if re.search(r"time box|base|ceiling|branch|worktree|scratch only|read-only", ln, re.I):
            print(f"  L{i}: {ln.strip()[:170]}")
