# Fold Wave 1 rows out of a full-tree extractor run into docs/metrics/.
# The extractor emits every session in the lead tree labelled with the
# requested wave; only the Wave 1 agent set below is appended. Old-wave
# rows are discarded (already committed from their own cutoff extracts).
# Spark Workflow children arrive labelled by session UUID; RELABEL maps
# them to their ledger names, attributed by first-prompt content and end
# stamps (f585e139 ends 05:44:48 = verifier-w1f64 ledger 05:44:40 and
# mentions verify-f64; f585e239 ends 05:50:22 = verifier-w1f32 05:49:50;
# 61085a45 mentions auditor-wave1). Lead is skipped: its session is
# cumulative across waves and cannot be delta-extracted by this tool.
import json
import pathlib
import sys

NEW = pathlib.Path("scratch/lead/metrics-w1-new")
DST = pathlib.Path("muse-softfloat/docs/metrics")
KEEP = {"parcel-f32", "parcel-f64", "regater-f32", "regater-f64"}
RELABEL = {
    "f585e139-e83b-7bbf-8089-e25f03d090b7": "verifier-w1f64",
    "f585e239-e83b-7d72-8089-e35f03d0926a": "verifier-w1f32",
    "61085a45-5b4a-753b-8cfb-eecea231f063": "auditor-wave1",
}
WORK = {
    "parcel-f32": "binary32 homogeneous core (173 instantiations)",
    "regater-f32": "binary32 homogeneous core (173 instantiations)",
    "parcel-f64": "binary64 homogeneous core (173 instantiations)",
    "regater-f64": "binary64 homogeneous core (173 instantiations)",
    "verifier-w1f32": "binary32 homogeneous core (173 instantiations)",
    "verifier-w1f64": "binary64 homogeneous core (173 instantiations)",
    "auditor-wave1": "methods adherence audit wave1",
}


def rows(path):
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def main():
    existing = {(r.get("wave"), r.get("agent")) for r in rows(DST / "passes.jsonl")}
    for fname in ("passes.jsonl", "usage.jsonl"):
        add = []
        for r in rows(NEW / fname):
            agent = r.get("agent")
            if agent in RELABEL:
                r["agent"] = RELABEL[agent]
                r["note"] = (r.get("note", "") + "; relabelled from session %s by lead fold (content+stamp attribution)" % agent).strip("; ")
                agent = r["agent"]
            if agent not in KEEP and agent not in RELABEL.values():
                continue
            if fname == "passes.jsonl":
                if (r.get("wave"), agent) in existing:
                    print("skip duplicate pass", agent)
                    continue
                if agent in WORK:
                    r["work"] = WORK[agent]
            add.append(r)
        if not add:
            print(fname, ": nothing appended")
            continue
        with (DST / fname).open("a") as f:
            for r in add:
                f.write(json.dumps(r, separators=(",", ":")) + "\n")
        print(fname, ": appended", [r["agent"] for r in add])
    return 0


if __name__ == "__main__":
    sys.exit(main())
