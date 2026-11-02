import json
rows = [
 dict(plant=1, shape="RTTZ arm rounds ties to even",
      note="F1: roundpack RTTZ==TE; verifier full 2^32 pairs-add 105,938,944 mismatches, every want==own ref; TE_HEAD mutant no-op"),
 dict(plant=2, shape="underflow dropped in the one inexact mul cell",
      note="F3: msf_aug.c:352 flag-only /10 vs /18; pool 542,720"),
 dict(plant=3, shape="exact-zero sum sign takes either operand",
      note="F2: || at msf_aug.c:277; exact-zero kinds 63,488 in full-op run"),
 dict(plant=4, shape="caller rounding attribute claimed for a fixed-rounding op",
      note="F5: operations.tsv mul=attr vs P4=fixed; official smoke fails at drift gate"),
 dict(plant=5, shape="R1 flags fabricated on an exact tiny residual",
      note="F4: aug-f64.vec:554 flags 18 vs 00; twin+generator+single-line regen diff"),
]
key = "ef5f9bd62893c48b46903daaaba8963aba401c333b70e72e69d01cde93b06830"
out = open("muse-softfloat/docs/metrics/plants.jsonl", "a")
for r in rows:
    r.update(wave="wave5", verifier="verifier-w5aug",
             work="SF-2 Step 4: augmented arithmetic",
             key_sha256=key, grade="caught", graded_by="lead",
             checked_by="lead-merge")
    ordered = {k: r[k] for k in ("wave","verifier","work","key_sha256","plant","shape","grade","graded_by","checked_by","note")}
    out.write(json.dumps(ordered) + "\n")
out.close()
allrows = [json.loads(l) for l in open("muse-softfloat/docs/metrics/plants.jsonl") if l.strip()]
print("plants total=%d caught=%d" % (len(allrows), sum(1 for r in allrows if r["grade"]=="caught")))
