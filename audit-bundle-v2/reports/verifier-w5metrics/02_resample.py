#!/usr/bin/env python3
"""Probe 2b: re-run the sanctioned extractor (from the copy, read-only) on a
spread of appended sessions; compare every number to its appended row."""
import json
import subprocess
import sys
from pathlib import Path

WS = Path("C:/Users/logan/source/repos/Muse-Softfloat")
COPY = WS / "worktrees/verify5-metrics"
STORE = Path("C:/Users/logan/.local/share/muse/sessions/2026/10/26/01a17907-4147-7333-a565-56071da9d971/subagent")
UNTIL = "2026-10-29T11:39:55-07:00"

sys.path.insert(0, str(COPY / "tools"))
import extract_session_metrics as E  # noqa: E402  (sanctioned extractor, copy)

until_micros = E.parse_until(UNTIL)


def rows(name, skip):
    out = subprocess.run(["git", "-C", str(COPY), "show", f"HEAD:docs/metrics/{name}"],
                         capture_output=True, check=True, text=True).stdout.splitlines()
    assert len(out) > skip, (name, len(out), skip)
    return [json.loads(l) for l in out[skip:]]


usage = rows("usage.jsonl", 39)
passes = rows("passes.jsonl", 39)
usage_by_agent = {r["agent"]: r for r in usage}
passes_by_agent = {}
for r in passes:
    passes_by_agent.setdefault(r["agent"], []).append(r)

# agent -> (sessions to sum for usage, sessions for pass span/tools, wave)
SAMPLE = {
    "verifier-sf0": (["41abe4fe-02c6-75f8-8ab1-4a474ba58c40"], None, "wave0"),
    "study-tier2-trigspike": (["13a14f54-6b13-7c63-81ea-938582d6f58b"], None, "wave4"),
    "verifier-sf1": (["d322adf0-83bd-73b6-82cd-8288d575c5ce",
                      "d322acf0-83bd-7203-82cd-8188d575c41b",
                      "d34d7516-1d09-749c-8c2b-f0cbe582aeb4",
                      "d34d7816-1d09-79b5-8c2b-f3cbe582b3cd",
                      "24110025-b6a7-7c1e-8700-bc5df2ed32e6"], None, "wave4"),
    "parcel-w5exp2": (["e9de5d3e-6484-7477-8c15-f73d944bf36f"], None, "wave5"),
    # verifier-w5exp2: usage sums both sessions; pass row in fact spans/sums
    # both too (row start=first-session start, tools=232+145=377) despite its
    # note claiming "second attempt's span set" -- checked as both here; the
    # note/row inconsistency is a finding.
    "verifier-w5exp2": (["700f06e4-82ff-7ae9-8f1d-a9f3bd9ca601",
                         "49570560-4959-7d33-8117-a2961016cd2b"],
                        None, "wave5"),
    "verifier-w5twiddledoc": (["fbd55c48-7762-7a93-86ce-54fa3966377b"], None, "wave5"),
    "study-tokens-visual": (["5a3949ba-ce42-7904-82c2-36f5ac6e9f9c"], None, "wave5"),
    "parcel-w5aug": (["90de2274-8655-7ebf-8201-3f30e813c537",
                      "dded10c5-1322-7b96-8793-784a56afe35e",
                      "7cc459bf-a202-7cf0-8448-2286d568ef88"], None, "wave5"),
}

fails = 0
for agent, (usess, psess, wave) in SAMPLE.items():
    psess = psess or usess
    extracted = []
    for s in usess:
        p = STORE / s / "session.jsonl"
        if not p.is_file():
            print(f"MISSING transcript file: {s}"); fails += 1; continue
        r = E.extract_session(p, False, wave, until_micros)
        if r is None:
            print(f"EXCLUDED by cutoff/internal: {agent} {s}"); fails += 1; continue
        extracted.append(r)
    # aggregate usage per model over usess
    agg = {}
    for r in extracted:
        for model, u in r["usage_by_model"].items():
            a = agg.setdefault(model, {"o": 0, "i": 0, "c": 0, "m": 0})
            a["o"] += u["output_tokens"]; a["i"] += u["input_tokens"]
            a["c"] += u["cached_tokens"]; a["m"] += r["messages_by_model"][model]
    urow = usage_by_agent[agent]
    model = urow["model"]
    ok = (len(agg) == 1 and model in agg)
    if not ok and len(agg) == 1:
        only = next(iter(agg))
        cross = all(agg[only][k] == urow[f] for k, f in
                    (("o", "output_tokens"), ("i", "input_tokens"),
                     ("c", "cached_tokens"), ("m", "messages")))
        print(f"{agent} CROSS-MODEL: row model={model} transcript model={only} "
              f"numbers_identical={cross}")
        fails += not cross  # numbers must still re-derive; label mismatch kept as finding
    got = agg.get(model, {})
    for k, f in (("o", "output_tokens"), ("i", "input_tokens"),
                 ("c", "cached_tokens"), ("m", "messages")):
        match = ok and got[k] == urow[f]
        print(f"{agent} usage.{f}: row={urow[f]} recomputed={got.get(k)} "
              f"{'MATCH' if match else 'MISMATCH'}")
        fails += not match
    # model attribution: extractor saw exactly the row's model
    print(f"{agent} model: row={model} extractor_models={sorted(agg)} "
          f"{'MATCH' if ok else 'MISMATCH'}")
    fails += not ok
    # passes row: tool_uses and span over psess
    prow = passes_by_agent[agent][0]
    pext = [r for r, s in zip(extracted, usess) if s in psess]
    tools = sum(r["tool_uses"] for r in pext)
    start = E.iso_local(min(r["start"] for r in pext))
    end = E.iso_local(max(r["end"] for r in pext))
    for label, rv, cv in (("tool_uses", prow["tool_uses"], tools),
                          ("start", prow["start"], start), ("end", prow["end"], end)):
        match = rv == cv
        print(f"{agent} pass.{label}: row={rv} recomputed={cv} {'MATCH' if match else 'MISMATCH'}")
        fails += not match
    # sha prefixes in note
    shas = [r["sha256"][:12] for r in extracted]
    shas_ok = all(s in prow["note"] for s in shas)
    print(f"{agent} note shas {shas}: {'all in note MATCH' if shas_ok else 'MISMATCH'}")
    fails += not shas_ok
    # role-label evidence: first started prompt head (counting only, first 200 chars)
    p0 = STORE / usess[0] / "session.jsonl"
    head = ""
    with open(p0, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            ev = (rec.get("payload") or {}).get("event") if isinstance(rec.get("payload"), dict) else None
            if isinstance(ev, dict) and ev.get("kind") == "started" and isinstance(ev.get("prompt"), str):
                head = ev["prompt"][:200]
                break
    print(f"{agent} first-prompt head: {head[:160]!r}")
    print("---")

print("RESAMPLE", "ALL MATCH" if fails == 0 else f"{fails} MISMATCHES")
sys.exit(1 if fails else 0)
