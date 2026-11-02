"""Independent derivation of every pinned expectation for the example.

Uses only integer / Fraction arithmetic (no library, no hardware
rounding except as a printed cross-check). Rounding a positive
rational to a binary format is done by scaling to an integer
significand and comparing the remainder with half an ulp.
"""
from fractions import Fraction
from decimal import Decimal, getcontext
import math
import struct


def round_rational(x, p, mode):
    """Round positive Fraction x to p-bit significand. Returns (M, E)
    with value M * 2^(E-p+1), 2^(p-1) <= M < 2^p. mode: te|tz."""
    assert x > 0
    # binary exponent: 2^e <= x < 2^(e+1)
    e = x.numerator.bit_length() - x.denominator.bit_length()
    while Fraction(2) ** e > x:
        e -= 1
    while Fraction(2) ** (e + 1) <= x:
        e += 1
    scale = (p - 1) - e  # x * 2^scale in [2^(p-1), 2^p)
    y = x * Fraction(2) ** scale if scale >= 0 else x / Fraction(2) ** (-scale)
    m, rem_num = divmod(y.numerator, y.denominator)
    rem = Fraction(rem_num, y.denominator)
    if mode == "tz":
        pass
    elif rem > Fraction(1, 2) or (rem == Fraction(1, 2) and m % 2 == 1):
        m += 1
        if m == 2 ** p:
            m //= 2
            e += 1
    return m, e


def pack(m, e, total_bits, exp_bits):
    p = total_bits - exp_bits  # incl. hidden bit: f64 53, f32 24
    frac_bits = p - 1
    bias = 2 ** (exp_bits - 1) - 1
    return ((e + bias) << frac_bits) | (m - 2 ** (p - 1))


def bits_of(x, total_bits, exp_bits, mode):
    p = total_bits - exp_bits
    m, e = round_rational(x, p, mode)
    exact = (Fraction(m) * Fraction(2) ** (e - p + 1)) == x
    return pack(m, e, total_bits, exp_bits), exact, m, e


def value_of(m, e, p):
    return Fraction(m) * Fraction(2) ** (e - p + 1)


def sqrt_bits(total_bits, exp_bits):
    """Correctly rounded (TE) sqrt(2) by integer square root."""
    p = total_bits - exp_bits
    # sqrt(2) in [1,2): e=0. Need M = round(sqrt(2) * 2^(p-1)).
    # Compute isqrt(2 * 2^(2(p-1)+2)) then round from 2 guard bits.
    g = 2
    n = 2 * 2 ** (2 * (p - 1) + 2 * g)
    r = math.isqrt(n)
    assert r * r < n < (r + 1) * (r + 1)  # sqrt2 irrational: no tie
    m, low = divmod(r, 2 ** g)
    # true value lies in (r, r+1) scaled; dropped fraction > low/4.
    # > half (2/4) iff low >= 2; low==2 means frac in (0.5, 0.75).
    if low >= 2:
        m += 1
    return pack(m, 0, total_bits, exp_bits), m


def dec_fixed(val, sig, mode):
    """Exact decimal string: Fraction val>0 rounded to sig significant
    digits (te=half-even, tz=toward zero), fixed notation."""
    getcontext().prec = 80
    d = Decimal(val.numerator) / Decimal(val.denominator)
    # find decimal exponent of leading digit
    e10 = d.adjusted()
    q = Decimal(1).scaleb(e10 - sig + 1)  # quantum
    from decimal import ROUND_HALF_EVEN, ROUND_DOWN
    r = d.quantize(q, rounding=ROUND_HALF_EVEN if mode == "te" else ROUND_DOWN)
    return format(r, "f")


tenth = Fraction(1, 10)
for (name, tb, eb) in [("f64", 64, 11), ("f32", 32, 8)]:
    for mode in ("te", "tz"):
        b, exact, m, e = bits_of(tenth, tb, eb, mode)
        sig = 17 if tb == 64 else 9
        print(f"div {name} 1/10 {mode}: bits={b:0{tb//4}x} exact={exact} "
              f"dec(sig={sig},{mode})={dec_fixed(value_of(m, e, tb - eb), sig, mode)}")

# exact product 1.5 * 2 = 3
b, exact, m, e = bits_of(Fraction(3), 64, 11, "te")
print(f"mul f64 1.5*2 te: bits={b:016x} exact={exact} "
      f"dec={dec_fixed(value_of(m, e, 53), 17, 'te')}")

for (name, tb, eb) in [("f64", 64, 11), ("f32", 32, 8)]:
    b, m = sqrt_bits(tb, eb)
    sig = 17 if tb == 64 else 9
    val = value_of(m, 0, tb - eb)
    print(f"sqrt {name} 2 te: bits={b:0{tb//4}x} dec(sig={sig})={dec_fixed(val, sig, 'te')}")

# augmented: a = 1 + 2^-23 (bits 3f800001); exact square decomposition
ma = 2 ** 23 + 1
prod = ma * ma  # value prod * 2^-46
print(f"aug: Ma={ma} prod={prod:#x} (value prod*2^-46)")
head_m = 2 ** 23 + 2  # 1 + 2^-22 at exponent 0 -> bits 3f800002
head_scaled = head_m * 2 ** 23  # head value * 2^46
tail_scaled = prod - head_scaled
print(f"aug: head_scaled={head_scaled:#x} tail_scaled={tail_scaled:#x} "
      f"tail_is_2^0_at_2^-46={tail_scaled == 1}")

# cross-checks only (host hardware): struct bits of literals
for v, fmt in [(1.0, "d"), (10.0, "d"), (2.0, "d"), (1.5, "d")]:
    print(f"lit f64 {v}: {struct.unpack('<Q', struct.pack('<d', v))[0]:016x}")
for v in (1.0, 10.0, 2.0):
    print(f"lit f32 {v}: {struct.unpack('<I', struct.pack('<f', v))[0]:08x}")
print(f"host f64 1/10: {struct.unpack('<Q', struct.pack('<d', 1.0/10.0))[0]:016x}")
print(f"host f32 1/10: {struct.unpack('<I', struct.pack('<f', 1.0/10.0))[0]:08x}")
# exact-integer construction of 10.0 bits (no host float): 10 = 1.25 * 2^3
for (name, tb, eb) in [("f64", 64, 11), ("f32", 32, 8)]:
    p = tb - eb
    m = 5 * 2 ** (p - 3)  # significand 1.01b * 2^(p-1)
    print(f"int-built {name} 10.0: {pack(m, 3, tb, eb):0{tb//4}x}")
