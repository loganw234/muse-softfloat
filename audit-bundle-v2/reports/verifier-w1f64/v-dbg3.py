import sys
from fractions import Fraction
src = open("scratch/verifier-w1f64/v-exact.py").read()
src = src.split("def rnorm64")[0]
exec(src)
X = 0x01000000000000
Y = 0xBFF0000000000001
dx = decode(X)
print("x cls=%s val=%s" % (dx["cls"], dx["val"]))
print("x == 2^-1026:", dx["val"] == Fraction(1, 2**1026))
for rm in ["te", "tz", "tp", "tn"]:
    print(rm, "%x %02x" % ref_div(X, Y, False, False, rm))
print("exact-neighbor %x %02x" % ref_div(0x0010000000000000, Y, False, False, "tn"))
print("one-ulp %x %02x" % ref_div(0x0000000000000001, Y, False, False, "tn"))
