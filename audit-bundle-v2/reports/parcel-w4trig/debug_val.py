from fractions import Fraction
import mpmath

mpmath.mp.dps = 80
bits = 0x0000523724D548C5
frac = bits & ((1 << 52) - 1)
x = Fraction(frac) * Fraction(2) ** -1074
y = mpmath.sinpi(mpmath.mpf(x.numerator) / x.denominator)
print("x ~", mpmath.nstr(mpmath.mpf(x.numerator) / x.denominator, 20))
print("y ~", mpmath.nstr(y, 30))
print("log2 y ~", float(mpmath.log(abs(y), 2)))
# nearest f64 and distance in ulps
import struct
def f64(v):
    return struct.unpack("<Q", struct.pack("<d", float(v)))[0]
b = f64(y)
print("nearest bits %016x" % b)
val = struct.unpack("<d", struct.pack("<Q", b))[0]
print("rel dist", mpmath.nstr(abs(y - mpmath.mpf(val)) / abs(y), 5), "log2", float(mpmath.log(abs(y-mpmath.mpf(val))/abs(y), 2)) if y != val else "exact")
