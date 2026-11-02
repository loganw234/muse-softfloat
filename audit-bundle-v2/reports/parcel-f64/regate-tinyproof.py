import sys
sys.path.insert(0, "worktrees/w1-f64/tests")
sys.stdout.reconfigure(encoding="utf-8")
import gen_vectors_f64 as g
from fractions import Fraction as F

def exact_val(fmt, bits):
    d = g.decode(fmt, bits)
    return d["val"]  # check key below if fails

# inspect decode keys
d = g.decode("f64", 0x000FFFFFFFFFFFFF)
print("decode keys:", sorted(d.keys()))
print(d)

cands = [
    (0x000FFFFFFFFFFFFF, 0x3FF0000000000001),
    (0x000FFFFFFFFFFFFF, 0xBFF0000000000001),
    (0x0010000000000001, 0x3FEFFFFFFFFFFFFE),
]
for a, b in cands:
    for rm in ("te", "ta", "tp", "tn", "tz"):
        r, f = g.ref_mul("f64", a, "f64", b, rm)
        print(f"mul {rm} {a:016x} {b:016x} -> {r:016x} flags={f:02x}")

# independent exact check for first candidate te
da = g.decode("f64", cands[0][0]); db = g.decode("f64", cands[0][1])
print("da", da)
print("db", db)
