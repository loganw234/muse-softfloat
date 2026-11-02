"""Cross-check the shipped project-exact reference
(tests/gen_vectors_aug.py) against the study probe
reference (scratch/sf2-augmented/ref_aug.py), which was
written from the clause extracts before the parcel.
Agreement required on bits and raised flags."""
import random
import sys

WS = __import__("pathlib").Path(__file__).resolve().parents[3]
sys.path.insert(0, str(WS / "worktrees" / "w5-aug" / "tests"))
sys.path.insert(0, str(WS / "scratch" / "sf2-augmented"))
import gen_vectors_aug as g
import ref_aug as s

FMTS = {"f16": s.F16, "f32": s.F32, "f64": s.F64}
FLAGBITS = {"invalid": 0x01, "overflow": 0x04,
            "underflow": 0x08, "inexact": 0x10}
rng = random.Random(20261029)
total = bad = 0
for fmt, sfmt in FMTS.items():
    pool = g.boundary_pool(fmt)
    cases = [(a, b, op) for a in pool for b in pool[::17] for op in g.OPS]
    bits = g.params(fmt)["bits"]
    for _ in range(4000):
        cases.append((rng.getrandbits(bits), rng.getrandbits(bits),
                      rng.choice(g.OPS)))
    for a, b, op in cases:
        h, t, fl, info = g.ref_augmented(fmt, a, b, op)
        r = s.augmented(sfmt, a, b, op)
        want_fl = 0
        for name in r["raise"]:
            want_fl |= FLAGBITS[name]
        total += 1
        # NaN payload from an sNaN input: ref_aug orig is
        # bits|qbit same-format, identical to 2.5 here.
        if (h, t, fl) != (r["head"], r["tail"], want_fl):
            bad += 1
            if bad <= 10:
                print("DISAGREE", fmt, op, hex(a), hex(b),
                      "shipped", hex(h), hex(t), fl,
                      "study", hex(r["head"]), hex(r["tail"]), want_fl,
                      r["kind"])
print("crosscheck total=%d disagreements=%d" % (total, bad))
