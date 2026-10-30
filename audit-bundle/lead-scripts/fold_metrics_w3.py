# Fold Wave 3 rows (method: fold_metrics_w1.py). Roles restated
# from ledgers where role_for() cannot know them. ias15-pico's
# reported tip is its branch head 361bf05 (merged d9718cf).
import json
import pathlib
import sys

NEW = pathlib.Path("scratch/lead/metrics-w3-new")
DST = pathlib.Path("muse-softfloat/docs/metrics")
KEEP = {"parcel-str", "ias15-pico", "verifier-w3str", "auditor-wave2"}
WORK = {
    "parcel-str": "decimal/hex character conversions (12 instantiations)",
    "verifier-w3str": "decimal/hex character conversions (12 instantiations)",
    "ias15-pico": "IAS15 Pico firmware + AEABI compat surface",
    "auditor-wave2": "methods adherence audit wave2",
}
PATCH = {
    "parcel-str": {"role": "author", "commit": "8712ec1fccdf25b1dc12c3cfa9c18de5e8de5869"},
    "ias15-pico": {"role": "author", "commit": "361bf05"},
    "verifier-w3str": {"role": "verifier", "a": 1, "b": 4, "verdict": "NOT READY", "sent_back": True},
}


def rows(path):
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def main():
    import subprocess
    PATCH["ias15-pico"]["commit"] = subprocess.check_output(
        ["git", "-C", "muse-softfloat", "rev-parse", "361bf05"]).decode().strip()
    existing = {(r.get("wave"), r.get("agent")) for r in rows(DST / "passes.jsonl")}
    for fname in ("passes.jsonl", "usage.jsonl"):
        add = []
        for r in rows(NEW / fname):
            agent = r.get("agent")
            if agent not in KEEP:
                continue
            if fname == "passes.jsonl":
                if (r.get("wave"), agent) in existing:
                    print("skip duplicate pass", agent)
                    continue
                if agent in WORK:
                    r["work"] = WORK[agent]
                if agent in PATCH:
                    r.update(PATCH[agent])
                    r["note"] = (r.get("note", "") + "; role/commit/verdict restated by lead fold from ledgers (extractor role_for gap)").strip("; ")
            add.append(r)
        if add:
            with (DST / fname).open("a") as f:
                for r in add:
                    f.write(json.dumps(r, separators=(",", ":")) + "\n")
        print(fname, ": appended", [r["agent"] for r in add])
    return 0


if __name__ == "__main__":
    sys.exit(main())
