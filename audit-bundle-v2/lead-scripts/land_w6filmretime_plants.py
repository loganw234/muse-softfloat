import json
from collections import Counter

rows = [
    dict(plant=1, shape="assembly duration table keeps the pre-retime why length",
         note="F1: SEGMENTS why 29.0 vs probed why3-1440p.mp4 32.00s; table native sum 182.0 not 185.0"),
    dict(plant=2, shape="assembly tempo scale is a no-op; cut would run 185 s over the cap",
         note="F1: tempo 120/120 (parent 120/124); duplicate-assembled product probed 185.00s > 180 cap, join checks sample scaled times not true cuts"),
    dict(plant=3, shape="idea BLOCKS audit ends the question beat at its own start",
         note="F2: _BGONE question=T_Q 21.5; imported computed BLOCKS give question dwells 0.0/-0.5 vs RULE 3.0/1.5 (renders unaffected)"),
    dict(plant=4, shape="phone-camera supersampling defaults off despite the SS=2 record",
         note="F4 (note): MSF_SS default 1 by import vs measurements3.json ss=2; shipped intro3 t=5.4 matches SS=2 re-render (MSE 3.4) not SS=1 (MSE 407.0)"),
    dict(plant=5, shape="kissfft gate holds one rank past its merge",
         note="F3: gate rank 70.0=G1_RANK+1.0 vs merge rank 69 from history.json; cursor_rank drops 70->69 at t=79.5 (non-monotonic)"),
]
key = "e3314462d753744df7c4757b305a360a4e9fda37f0bc0aa9c60a26f34e72a777"
path = "muse-softfloat/docs/metrics/plants.jsonl"
before = open(path, "rb").read()
assert b"verifier-w6filmretime" not in before
with open(path, "ab") as out:
    if not before.endswith(b"\n"):
        out.write(b"\n")
    for r in rows:
        r.update(wave="wave6", verifier="verifier-w6filmretime",
                 work="Wave 6 film retime: dedupe question, SS=2 phone zoom, 3-minute cap",
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
print("wave6 total=%d caught=%d verifiers=%s" % (
    len(w6), sum(1 for r in w6 if r["grade"] == "caught"),
    sorted(Counter(r["verifier"] for r in w6).items())))
