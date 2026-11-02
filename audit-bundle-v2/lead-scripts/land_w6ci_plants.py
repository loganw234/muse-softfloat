import json

rows = [
    dict(plant=1, shape="standard CI job silently runs only the smoke budget",
         note="F2: step named merge gate runs run.sh smoke; exhaustive legs never run (+F4 artefact path consequence)"),
    dict(plant=2, shape="standard job moved off Linux, defeating the parcel purpose",
         note="F1: runs-on windows-latest while steps sudo apt-get"),
    dict(plant=3, shape="MSYS2 PATH guard inverted",
         note="F5: [! -d] vs its own comment; plain host run FAILs compiler REFUSED i686"),
    dict(plant=4, shape="CRLF last-field bug reintroduced in the nan control",
         note="F7: $NF== compare gives 0 diff bytes in binary mode; WSL gate NOT REFUSED reproduced"),
    dict(plant=5, shape="expect-count provenance tags printed CR-carrying again",
         note="F6: print $NF yields 10 CR-carrying tags on the Linux channel; OLD==NEW byte-identical"),
]
key = "c33726a7b2833b50653b75d7473ac65d501403c5c2a460f4397be355f7806ab8"
path = "muse-softfloat/docs/metrics/plants.jsonl"
before = open(path, "rb").read()
assert b"verifier-w6ci" not in before
with open(path, "ab") as out:
    if not before.endswith(b"\n"):
        out.write(b"\n")
    for r in rows:
        r.update(wave="wave6", verifier="verifier-w6ci",
                 work="Wave 6: library CI on Linux (GitHub Actions)",
                 key_sha256=key, grade="caught", graded_by="lead",
                 checked_by="lead-merge")
        ordered = {k: r[k] for k in ("wave", "verifier", "work", "key_sha256",
                                      "plant", "shape", "grade", "graded_by",
                                      "checked_by", "note")}
        out.write((json.dumps(ordered) + "\n").encode("utf-8"))
after = open(path, "rb").read()
assert after[:len(before)] == before
allrows = [json.loads(x) for x in after.decode("utf-8").splitlines() if x.strip()]
print("plants total=%d caught=%d" % (
    len(allrows), sum(1 for r in allrows if r["grade"] == "caught")))
