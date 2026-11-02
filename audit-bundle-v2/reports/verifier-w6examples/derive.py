"""Independent exact-rational derivation of every number in examples/host."""
from fractions import Fraction as F
import struct

ok = True
def check(name, got, want):
    global ok
    s = "OK " if got == want else "MISMATCH "
    if got != want:
        ok = False
    print(f"{s}{name}: derived={got} claimed={want}")

def f64bits(b):
    return struct.unpack('<d', struct.pack('<Q', b))[0]
def f32bits(b):
    return struct.unpack('<f', struct.pack('<I', b))[0]
def Fof64(b): return F(f64bits(b))
def Fof32(b): return F(f32bits(b))

# --- 1/10 binary64: bracket exact quotient between adjacent doubles
q = F(1, 10)
a = 0x3FB9999999999999  # candidate TZ
b = 0x3FB999999999999A  # candidate TE
c = 0x3FB999999999999B  # main.c TE claim
check("f64 TZ below q", Fof64(a) < q < Fof64(b), True)
check("f64 TE nearest", abs(Fof64(b) - q) < abs(Fof64(a) - q), True)
check("f64 TE even-mantissa", (b & 1) == 0, True)
check("f64 main.c ...9b above TE", c == b + 1, True)
check("f64 diff exactly one ulp", b - a == 1, True)

# --- 1/10 binary32
a32 = 0x3DCCCCCC; b32 = 0x3DCCCCCD
check("f32 TZ below q", Fof32(a32) < q < Fof32(b32), True)
check("f32 TE nearest", abs(Fof32(b32) - q) < abs(Fof32(a32) - q), True)
check("f32 TE even-mantissa", (b32 & 1) == 0, True)
check("f32 one-ulp apart", b32 - a32 == 1, True)

# --- 1.5*2 exact
check("f64 1.5*2 bits", F(Fof64(0x4008000000000000)) == F(3), True)
check("mul expected ...001 wrong", 0x4008000000000001 != 0x4008000000000000, True)
check("...001 value above 3", Fof64(0x4008000000000001) > 3, True)

# --- sqrt2: verify claimed patterns bracket sqrt(2) with correct rounding
for b, nxt, fmt in ((0x3FF6A09E667F3BCD, 1, 64), (0x3FB504F3, 1, 32)):
    v = Fof64(b) if fmt == 64 else Fof32(b)
    vlo = v
    vb = Fof64(b + 1) if fmt == 64 else Fof32(b + 1)
    va = Fof64(b - 1) if fmt == 64 else Fof32(b - 1)
    two = F(2)
    # correctly rounded sqrt: v^2 nearest to 2 among neighbors
    dv, da, db = abs(vlo * vlo - two), abs(va * va - two), abs(vb * vb - two)
    check(f"{'f64' if fmt==64 else 'f32'} sqrt nearest", dv < da and dv <= db, True)
    print(f"   info: dv={float(dv):.3e} da={float(da):.3e} db={float(db):.3e}")

# --- augmented pair: head + tail == exact a*a with a = 1+2^-23
a = 0x3F800001
ma = (a & 0x7FFFFF) | 0x800000  # 2^23+1
ea = -23
prod = ma * ma
mh, eh = (0x3F800002 & 0x7FFFFF) | 0x800000, -23
mt, et = (0x28800000 & 0x7FFFFF) | 0x800000, 81 - 127 - 23
check("aug tail exp", et == -69, True)
check("aug exact sum", (mh << 23) + (mt >> 23) == prod, True)
check("aug prod hex", format(prod, 'x') == '400001000001', True)
check("aug head value 1+2^-22", F(mh) * F(2) ** eh == 1 + F(2) ** -22, True)
check("aug tail value 2^-46", F(mt) * F(2) ** et == F(2) ** -46, True)
check("aug a*a identity", (1 + F(2) ** -23) ** 2 == 1 + F(2) ** -22 + F(2) ** -46, True)

# --- 0/0
z = 0x7FF8000000000000
check("qnan exp all-ones frac nonzero", ((z >> 52) & 0x7FF) == 0x7FF and (z & 0xFFFFFFFFFFFFF) != 0, True)

# --- decimal strings: 17/9 sig-digit fixed rendering of the binary value
from decimal import Decimal, getcontext
getcontext().prec = 80
def dec_fixed(frac, sig):
    # fixed style with `sig` significant digits: position point accordingly
    d = Decimal(frac.numerator) / Decimal(frac.denominator)
    adj = d.adjusted()  # exponent of most significant digit
    places = sig - 1 - adj
    q = Decimal(1).scaleb(-places)
    return str(d.quantize(q))
check("dec f64 TE", dec_fixed(Fof64(0x3FB999999999999A), 17), "0.10000000000000001")
check("dec f64 TZ", dec_fixed(Fof64(0x3FB9999999999999), 17), "0.099999999999999991")
check("dec f32 TE", dec_fixed(Fof32(0x3DCCCCCD), 9), "0.100000001")
check("dec f32 TZ", dec_fixed(Fof32(0x3DCCCCCC), 9), "0.0999999940")
check("dec f64 3.0", dec_fixed(F(3), 17), "3.0000000000000000")
check("dec f64 sqrt2", dec_fixed(Fof64(0x3FF6A09E667F3BCD), 17), "1.4142135623730951")
check("dec f32 sqrt2", dec_fixed(Fof32(0x3FB504F3), 9), "1.41421354")

print()
print("DERIVATION", "ALL-OK" if ok else "FAILURES-PRESENT")
