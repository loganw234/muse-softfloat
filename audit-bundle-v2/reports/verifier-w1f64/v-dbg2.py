import sys
from fractions import Fraction
sys.path.insert(0, "scratch/verifier-w1f64")
src = open("scratch/verifier-w1f64/v-exact.py").read()
src = src.split("def rnorm64")[0]
exec(src)
v = Fraction(1, 2) * pow2(5000)
print("v>0:", v > 0)
print("pack %x %02x" % pack_frac(v, 0, "tz"))
m = v
e = m.numerator.bit_length() - m.denominator.bit_length()
print("e =", e)
