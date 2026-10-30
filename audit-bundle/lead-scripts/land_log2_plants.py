import json
rows = [
 dict(plant=1, shape="recentring compare widened past the exact square boundary",
      note="F1: >= at msf_math.c:1424; log2(1.0) garbage+inexact, powers inexact; two deciders agree f16 310"),
 dict(plant=2, shape="binary64 log error bound narrowed past its proof",
      note="F2: EK_LOG[2]=300 vs generator-proven 370, twin regen byte-identical"),
 dict(plant=3, shape="generator underflow flag bit wrong",
      note="F4: UNDERFLOW=0x04 at gen_vectors_explog.py:58; generation refuses; 0x08 restore byte-identical"),
 dict(plant=4, shape="implemented row drops the fifth attribute",
      note="F3: msf64_log2p1 wave-4 vs operations wave-5 trips gen_tables assert; generated files cannot re-derive"),
 dict(plant=5, shape="pole divide-by-zero stripped from committed vector",
      note="F5: explog-f64.vec:25369 log2p1(-1) flag 00 vs correct 02"),
]
key = "d5ff8180a7525e11639ad26fa5bc8ab6655a872401c52dd5a8a0d8f17cd9299d"
out = open("muse-softfloat/docs/metrics/plants.jsonl", "a")
for r in rows:
    r.update(wave="wave5", verifier="verifier-w5log2",
             work="SF-2 Step 3b: log2/log2p1",
             key_sha256=key, grade="caught", graded_by="lead",
             checked_by="lead-merge")
    ordered = {k: r[k] for k in ("wave","verifier","work","key_sha256","plant","shape","grade","graded_by","checked_by","note")}
    out.write(json.dumps(ordered) + "\n")
out.close()
allrows = [json.loads(l) for l in open("muse-softfloat/docs/metrics/plants.jsonl") if l.strip()]
print("plants total=%d caught=%d" % (len(allrows), sum(1 for r in allrows if r["grade"]=="caught")))
