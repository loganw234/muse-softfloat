import json
rows = [
 dict(plant=1, shape="ungated N=256 inverse coverage claimed",
      note="F4: driver twiddle_gate.c:169-170 fwd-only at N=256"),
 dict(plant=2, shape="field census total inflated",
      note="F1: 8956 vs recomputed 4096+3072+448+344+512+384=8856"),
 dict(plant=3, shape="never-unmodified rule inverted",
      note="F3: 'claimed wherever convenient' vs all authorities"),
 dict(plant=4, shape="decider precision halved in the record",
      note="F5: '128-bit choice' for the 256-bit MPFR decider"),
 dict(plant=5, shape="retained-derivation link broken",
      note="F7: BOARD.md link ../TWIDDLE.md target missing"),
]
key = "2cf0f2c7641add7367ecfa85965a13eeff129e80f7e2aaa7bab6e2249f9063e7"
out = open("muse-softfloat/docs/metrics/plants.jsonl", "a")
for r in rows:
    r.update(wave="wave5", verifier="verifier-w5twiddledoc",
             work="MPFR twiddle derivation retained (docs/TWIDDLES.md)",
             key_sha256=key, grade="caught", graded_by="lead",
             checked_by="lead-merge")
    # order keys like existing rows
    ordered = {k: r[k] for k in ("wave","verifier","work","key_sha256","plant","shape","grade","graded_by","checked_by","note")}
    out.write(json.dumps(ordered) + "\n")
out.close()
