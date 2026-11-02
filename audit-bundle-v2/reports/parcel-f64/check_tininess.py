import sys
sys.path.insert(0,"worktrees/w1-f64/tests")
sys.stdout.reconfigure(encoding="utf-8")
import gen_vectors_f64 as g
from fractions import Fraction as F
# Berkeley mul case: min_normal * (1-2^-53) -> min_normal, Berkeley flags 0x18
a=g.ref_mul("f64",0x0010000000000000,"f64",0x3fefffffffffffff,"te")
print("mul boundary", hex(a[0]), hex(a[1]), "want minnormal/18")
# lead second shape transposed: value that rounds at p bits unbounded to exactly 2^emin
# (2^104-1)*2^-2126? construct exact Fraction just below min normal but p-bit rounding goes up
v=(F(2)**53-1)*F(2)**(-1075)  # (1-2^-53)*2^-1022 inexact subnormal delivery?
print("v pack te", [hex(x) for x in g.pack_value(v,"te")])
# value = 2^-1022 - 2^-1076 (above halfway in unbounded binade spacing 2^-1075)
v2=F(2)**-1022 - F(2)**-1076
print("v2 pack te", [hex(x) for x in g.pack_value(v2,"te")], "unbounded rounds to minnormal => expect no UF")
# exact subnormal no flags
print("exact sub", [hex(x) for x in g.pack_value(F(2)**-1074*3,"te")])
# tiny inexact below
print("tiny inexact", [hex(x) for x in g.pack_value(F(2)**-1075*3,"te")])
