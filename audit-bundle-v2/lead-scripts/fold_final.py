# Fold video-final + auditor-final rows from the w3 extract tree
# (re-extract first if metrics-w3-new predates them: the caller
# re-runs extract_w3.ps1 with a later --until before this).
import json
import pathlib
import sys

NEW = pathlib.Path("scratch/lead/metrics-final-new")
DST = pathlib.Path("muse-softfloat/docs/metrics")
KEEP = {"video-final": "demo video final render", "auditor-final": "methods adherence audit final"}


def rows(p):
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


existing_p = {(r.get("wave"), r.get("agent")) for r in rows(DST / "passes.jsonl")}
existing_u = {(r.get("wave"), r.get("agent")) for r in rows(DST / "usage.jsonl")}
for fname, existing in (("passes.jsonl", existing_p), ("usage.jsonl", existing_u)):
    add = []
    for r in rows(NEW / fname):
        if r.get("agent") not in KEEP:
            continue
        if (r.get("wave"), r["agent"]) in existing:
            print("skip dup", fname, r["agent"])
            continue
        if fname == "passes.jsonl":
            r["work"] = KEEP[r["agent"]]
        add.append(r)
    if add:
        with (DST / fname).open("a") as f:
            for r in add:
                f.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(fname, [r["agent"] for r in add])
