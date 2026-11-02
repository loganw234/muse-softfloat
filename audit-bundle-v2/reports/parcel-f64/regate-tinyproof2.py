import sys
sys.path.insert(0, "worktrees/w1-f64/tests")
sys.stdout.reconfigure(encoding="utf-8")
import gen_vectors_f64 as g
from fractions import Fraction as F

def value(bits):
    d = g.decode("f64", bits)
    v = F(d["sig"]) * (F(2) ** d["exp"])
    return -v if d["sign"] else v

def analyse(name, a, b):
    va, vb = value(a), value(b)
    exact = va * vb
    emin = F(2) ** -1022
    print(f"{name}: exact={exact}  exact<2^emin: {abs(exact) < emin}")
    # unbounded p=53 rounding (te) via generator pack is restated ref;
    # manual: scale to binade of exact
    print(f"  pack_value te -> {[hex(x) for x in g.pack_value(exact, 'te')]}")
    r, f = g.ref_mul("f64", a, "f64", b, "te")
    print(f"  ref_mul te -> {r:016x} flags={f:02x}")

# Shape 1 (arith line 1824): both before and unbounded-after say tiny
analyse("line1824", 0x3FEFFFFFFFFFFFFF, 0x0010000000000000)
# Shape 2 (Berkeley mul te line 1190): before says tiny, unbounded-after says not tiny
analyse("berkeley1190", 0x000FFFFFFFFFFFFF, 0x3FF0000000000001)
# manual exact fractions
v1 = (F(2)**53 - 1) * F(2)**-1075
print("line1824 exact closed form (2^53-1)*2^-1075 matches:", value(0x3FEFFFFFFFFFFFFF)*value(0x0010000000000000) == v1)
v2 = (F(2)**52 - 1) * F(2)**-1074 * (1 + F(2)**-52)
print("berkeley1190 exact closed form matches:", value(0x000FFFFFFFFFFFFF)*value(0x3FF0000000000001) == v2)
print("v2 = 2^-1022 - 2^-1074 + (2^52-1)*2^-1126 ; check:", v2 == F(2)**-1022 - F(2)**-1074 + (F(2)**52-1)*F(2)**-1126)
