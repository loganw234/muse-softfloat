import json
rows = [
 dict(plant=1, shape="underflow cut swallows the exact tie input",
      note="F1: cut <= at msf_math.c E_tie gives +0 not u in ta, all formats (one-cell probes)"),
 dict(plant=2, shape="stage-3 error bound narrowed past its proof",
      note="F2: committed EK {147,243,200} vs generator-proven {147,243,371}, double regen deterministic"),
 dict(plant=3, shape="generator inexact flag bit wrong",
      note="F5: INEXACT=0x08 in gen_vectors_explog.py; regen refuses TABLE DISAGREE"),
 dict(plant=4, shape="exp2m1 row claims no exception flags",
      note="F3: operations.tsv flags=no vs generated yes; gen_tables 3-file drift"),
 dict(plant=5, shape="inexact fabricated on an exact specials vector",
      note="F4: explog-f64.vec:4 te -0 flags 10 vs correct 00"),
]
key = "8e186bd5c7b606ec16766d326651250bb62af22d5658f4403378fc7161c7d611"
out = open("muse-softfloat/docs/metrics/plants.jsonl", "a")
for r in rows:
    r.update(wave="wave5", verifier="verifier-w5exp2",
             work="SF-2 Step 3a: exp2/exp2m1",
             key_sha256=key, grade="caught", graded_by="lead",
             checked_by="lead-merge")
    ordered = {k: r[k] for k in ("wave","verifier","work","key_sha256","plant","shape","grade","graded_by","checked_by","note")}
    out.write(json.dumps(ordered) + "\n")
out.close()
allrows = [json.loads(l) for l in open("muse-softfloat/docs/metrics/plants.jsonl") if l.strip()]
print("plants total=%d caught=%d" % (len(allrows), sum(1 for r in allrows if r["grade"]=="caught")))
