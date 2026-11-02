#!/usr/bin/env python3
"""Probe 3A (corrected): every appended author/fixer commit must exist in the
copy history AND be the second parent of a landing merge (the parcel tip),
except parcel-w5twiddledoc pass 1 which rule 5 of ledger/parcel-w5metrics.md
explicitly cites as the pre-fix mainline commit. Also checks a RECORD or
parcel-ledger citation (7+ char prefix)."""
import json
import subprocess
from pathlib import Path

WS = Path("C:/Users/logan/source/repos/Muse-Softfloat")
COPY = WS / "worktrees/verify5-metrics"


def git(*args):
    r = subprocess.run(["git", "-C", str(COPY)] + list(args),
                       capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def rows(name, skip):
    rc, out, _ = git("show", f"HEAD:docs/metrics/{name}.jsonl")
    assert rc == 0
    return [json.loads(l) for l in out.splitlines()[skip:]]


passes = rows("passes", 39)
rc, merges, _ = git("log", "--merges", "--format=%H %P")
mergelines = merges.splitlines()
second_parents = {}
for m in mergelines:
    f = m.split()
    if len(f) >= 3:
        second_parents.setdefault(f[2], []).append(f[0][:7])
rec = (WS / COPY / "docs/RECORD.md").read_text(encoding="utf-8", errors="replace")
led = {p.name: p.read_text(encoding="utf-8", errors="replace")
       for p in (WS / "ledger").glob("parcel-*.md")}
led["parcel-w5metrics.md"] = (WS / "ledger/parcel-w5metrics.md").read_text(encoding="utf-8", errors="replace")
fails = 0
for r in passes:
    if r["role"] not in ("author", "fixer"):
        continue
    c, agent = r["commit"], r["agent"]
    rc, _, _ = git("cat-file", "-e", c)
    if rc != 0:
        print(f"{agent}: commit {c[:12]} MISSING"); fails += 1; continue
    rc, _, _ = git("merge-base", "--is-ancestor", c, "HEAD")
    is_anc = rc == 0
    as2nd = second_parents.get(c, [])
    cited = [n for n, t in ({"RECORD.md": rec} | led).items()
             if c in t or c[:12] in t or c[:7] in t]
    if not cited and as2nd:
        # RECORD may cite the landing merge whose message names the tip.
        for m7 in as2nd:
            rc, msg, _ = git("log", "-1", "--format=%B", m7)
            if rc == 0 and (c in msg or c[:7] in msg) and (
                    m7 in rec or any(m7 in t for t in led.values())):
                cited = [f"RECORD.md via merge {m7}"]
                break
    ok_shape = bool(as2nd) or (agent == "parcel-w5twiddledoc" and r["pass"] == 1)
    status = "OK" if (ok_shape and is_anc and cited) else "CHECK"
    if status == "CHECK":
        fails += 1
    print(f"{agent} pass{r['pass']}: tip->merge2nd={as2nd or 'NONE'} ancestor={is_anc} "
          f"cited={cited or 'NONE'} {status}")
print("AUTHORS", "ALL TRACE" if fails == 0 else f"{fails} TO CHECK")
raise SystemExit(1 if fails else 0)
