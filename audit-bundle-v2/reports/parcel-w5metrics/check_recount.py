#!/usr/bin/env python3
"""Recount check: extractor (until SF-2 close) vs frozen rows, per session."""
import json
import re
from pathlib import Path

WS = Path(r"C:\Users\logan\source\repos\Muse-Softfloat")
HERE = Path(__file__).parent
SID = re.compile(r"session ([0-9a-f-]{36})")


def load(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def by_session(rows):
    out = {}
    for r in rows:
        m = SID.search(r.get("note", ""))
        if m:
            out[m.group(1)] = r
    return out


fz_u = by_session(load(WS / "worktrees/w5-metrics/docs/metrics/usage.jsonl"))
fz_p = by_session(load(WS / "worktrees/w5-metrics/docs/metrics/passes.jsonl"))
ex_u = by_session(load(HERE / "extract-out/usage.jsonl"))
ex_p = by_session(load(HERE / "extract-out/passes.jsonl"))
print(f"frozen usage sessions={len(fz_u)} passes={len(fz_p)}; extract usage={len(ex_u)} passes={len(ex_p)}")
exact = diff = 0
for sid in sorted(fz_u, key=lambda s: fz_p[s]["start"]):
    fu, fp = fz_u[sid], fz_p[sid]
    eu, ep = ex_u.get(sid), ex_p.get(sid)
    if eu is None:
        print(f"MISSING-IN-EXTRACT {sid} {fu['agent']}")
        diff += 1
        continue
    dus = []
    for f in ("output_tokens", "input_tokens", "cached_tokens", "messages"):
        if fu.get(f) != eu.get(f):
            dus.append(f"{f}: frozen={fu.get(f)} recount={eu.get(f)}")
    for f in ("start", "end", "tool_uses"):
        if fp.get(f) != ep.get(f):
            dus.append(f"{f}: frozen={fp.get(f)} recount={ep.get(f)}")
    # transcript sha: frozen note has sha256 XXX12; compare if present
    m1 = re.search(r"sha256 ([0-9a-f]{12})", fp.get("note", ""))
    m2 = re.search(r"sha256 ([0-9a-f]{12})", ep.get("note", ""))
    sha_same = bool(m1 and m2 and m1.group(1) == m2.group(1))
    if dus:
        diff += 1
        print(f"DIFF {fu['agent']} {sid} sha_same={sha_same}")
        for d in dus:
            print(f"     {d}")
    else:
        exact += 1
print(f"exact={exact} diff={diff} of {len(fz_u)} (lead main excluded from exact expectation: live file, frozen used an earlier --until)")
new = [s for s in ex_u if s not in fz_u]
print(f"new sessions in extract: {len(new)}")
