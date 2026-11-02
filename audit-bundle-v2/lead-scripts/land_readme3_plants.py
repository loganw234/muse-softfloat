import json
rows = [
 dict(plant=1, shape="headline instantiation count inflated by ten",
      note="F1: README 859 vs COVERAGE recount 849=783+66"),
 dict(plant=2, shape="augmented op-count benefit claimed as shipped",
      note="F2: README line inverts RECORD study-model labelling"),
 dict(plant=3, shape="site claims every plant ever caught",
      note="F4: data.json 115/115 vs recount 109/115, contradicts own by-wave rows"),
 dict(plant=4, shape="augmented pair exclusion erased from the numbers table",
      note="F3+F6: pair_excluded 0 vs 9; 822+0+18 != 849; rendered table broken"),
 dict(plant=5, shape="site sample exp2(0) expectation off by one ulp",
      note="F5+F7: sample idx1258 ...0001 vs .vec/wasm ...0000; replay 0-mismatch claim irreproducible"),
]
key = "17ae218eb70d3a79989c974c18c0f6b3218ddf699927d549da516b5728103419"
out = open("muse-softfloat/docs/metrics/plants.jsonl", "a")
for r in rows:
    r.update(wave="wave5", verifier="verifier-w5readme3",
             work="Wave 5 close: README + site refresh",
             key_sha256=key, grade="caught", graded_by="lead",
             checked_by="lead-merge")
    ordered = {k: r[k] for k in ("wave","verifier","work","key_sha256","plant","shape","grade","graded_by","checked_by","note")}
    out.write(json.dumps(ordered) + "\n")
out.close()
allrows = [json.loads(l) for l in open("muse-softfloat/docs/metrics/plants.jsonl") if l.strip()]
print("plants total=%d caught=%d" % (len(allrows), sum(1 for r in allrows if r["grade"]=="caught")))
