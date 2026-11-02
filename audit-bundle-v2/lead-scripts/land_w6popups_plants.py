import json
from collections import Counter

rows = [
    dict(plant=1, shape="parcels card counts the lead spine pass as a parcel",
         note="F1: code 20 vs drawn author lanes 19 (spine E001 is lead wave0, passes_role author); mp4/ledger/row read 19"),
    dict(plant=2, shape="verifiers card carries the studies count",
         note="F2: code 35 vs 36 verifier lanes drawn (passes verifier=36); mp4/ledger/row read 36"),
    dict(plant=3, shape="plants card uses the post-freeze HEAD total",
         note="F3: code 155 = HEAD mechanical total (148 caught + 7 missed) vs frozen graph accounting plants_rows 150; discipline requires 150"),
    dict(plant=4, shape="gates card transposes digits in the standard extras total",
         note="F4: code 1,171,504 vs generator parts 917504+200000=1,117,504, RECORD and live verify-standard.log total agree"),
    dict(plant=5, shape="studies card breaks its word budget; dwell and downstream timings move",
         note="F5: 7-word line makes POPUP_WORDS [7,9,8,8,11,11,9] vs base 9 on studies; import dump TOTAL 108.5 vs sealed 108.0, dwell/arrivals/shift all differ"),
]
key = "9e0d129db51ecbda7dcd120afc713a6984d1b4a2237a5ca033dd6f64e087af8a"
path = "muse-softfloat/docs/metrics/plants.jsonl"
before = open(path, "rb").read()
assert b"verifier-w6popups" not in before
with open(path, "ab") as out:
    if not before.endswith(b"\n"):
        out.write(b"\n")
    for r in rows:
        r.update(wave="wave6", verifier="verifier-w6popups",
                 work="Wave 6 popup cards generalised with project totals",
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
w6 = [r for r in allrows if r["wave"] == "wave6"]
print("wave6 total=%d caught=%d verifiers=%d" % (
    len(w6), sum(1 for r in w6 if r["grade"] == "caught"),
    len(Counter(r["verifier"] for r in w6))))
