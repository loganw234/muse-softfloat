# Fold Wave 2 rows from the full-tree extract (see fold_metrics_w1.py
# for the method). Spark verifiers arrive as session UUIDs:
# 8186e594 ends 08:08:39 and works verify2-f16; 8186e494 ends
# 08:11:37 and works verify2-xf. Roles restated from ledgers where
# the extractor's role_for() cannot know them (parcel-* are authors;
# ias15-port and video-tools delivered commits-less work products in
# scratch/video and stay surveyor-class passes). Lead skipped
# (cumulative session, not delta-extractable).
import json
import pathlib
import sys

NEW = pathlib.Path("scratch/lead/metrics-w2-new")
DST = pathlib.Path("muse-softfloat/docs/metrics")
KEEP = {"parcel-f16", "parcel-xf", "ias15-port", "video-tools"}
RELABEL = {
    "8186e594-fc47-70a6-84ff-2753e0c6f35e": "verifier-w2f16",
    "8186e494-fc47-7ef3-84ff-2653e0c6f1ab": "verifier-w2xf",
}
WORK = {
    "parcel-f16": "binary16 homogeneous core (236 instantiations)",
    "verifier-w2f16": "binary16 homogeneous core (236 instantiations)",
    "parcel-xf": "cross-format binary32/64 with binary16 sources (126 instantiations)",
    "verifier-w2xf": "cross-format binary32/64 with binary16 sources (126 instantiations)",
    "ias15-port": "IAS15 host feasibility proof",
    "video-tools": "demo video tooling",
}
PATCH = {
    "parcel-f16": {"role": "author", "commit": "44c770c7c57a394685f9a9a9bc3069ccd98af78a"},
    "parcel-xf": {"role": "author", "commit": "7935fabe737e387b39f6eebb224c19d8074d4498"},
    "verifier-w2f16": {"role": "verifier", "a": 1, "b": 4, "verdict": "NOT READY", "sent_back": True},
    "verifier-w2xf": {"role": "verifier", "a": 3, "b": 3, "verdict": "NOT READY", "sent_back": True},
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
