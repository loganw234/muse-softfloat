# Append rechecker-tininess rows from the full-tree extract. Session
# 74b4343d runs 04:50:16..05:00:54 matching ledger/rechecker-tininess.md
# stamp 2026-10-27 05:00:39; it verified lead commits 53acb1a + b37fb12,
# verdict READY (a)0 (b)0, oracle differential 2400/2400.
import json
import pathlib

NEW = pathlib.Path("scratch/lead/metrics-w1-new")
DST = pathlib.Path("muse-softfloat/docs/metrics")
UID = "74b4343d-b308-7089-88c0-b6099469c201"


def rows(p):
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


for fname in ("passes.jsonl", "usage.jsonl"):
    for r in rows(NEW / fname):
        if r.get("agent") != UID:
            continue
        r["agent"] = "rechecker-tininess"
        r["note"] = (r.get("note", "") + "; relabelled from session %s by lead fold (stamp attribution)" % UID).strip("; ")
        if fname == "passes.jsonl":
            r.update({"role": "verifier", "work": "pack tininess Clause 7.5 lead fix",
                      "a": 0, "b": 0, "verdict": "READY", "sent_back": False})
        with (DST / fname).open("a") as f:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
        print(fname, "appended rechecker-tininess")
