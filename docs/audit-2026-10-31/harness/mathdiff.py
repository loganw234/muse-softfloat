"""Independent oracle for the Clause 9 functions: mpmath at 256 bits, exact-rational rounding
in all five modes with tininess after rounding. usage: mathdiff.py DRIVER FMT N_PER_OP [exhaustive]"""
import sys, random, subprocess, math
from fractions import Fraction
import mpmath
from mpmath import mp
mp.prec = 320
DRIVER, FMT, N = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); EXH = len(sys.argv) > 4
random.seed(20261031 + FMT)
INV, DBZ, OVF, UNF, INX = 1, 2, 4, 8, 16
P = {16: (11, -14, 15, 15, 10, 16), 32: (24, -126, 127, 127, 23, 32), 64: (53, -1022, 1023, 1023, 52, 64)}[FMT]
p, emin, emax, bias, fbits, width = P
MODES = [0, 1, 2, 3, 4]
def decode(u):
    s = u >> (width - 1); e = (u >> fbits) & ((1 << (width - fbits - 1)) - 1); m = u & ((1 << fbits) - 1)
    emaxf = (1 << (width - fbits - 1)) - 1
    if e == emaxf: return None  # inf/nan
    if e == 0: v = Fraction(m, 1 << fbits) * Fraction(2) ** emin
    else: v = (1 + Fraction(m, 1 << fbits)) * Fraction(2) ** (e - bias)
    return -v if s else v
def encode(v, s):
    """v: non-negative Fraction exactly representable (incl. subnormal/zero); s: sign"""
    if v == 0: return s << (width - 1)
    if v < Fraction(2) ** emin:
        mant = v / Fraction(2) ** (emin - fbits); assert mant.denominator == 1
        return (s << (width - 1)) | mant.numerator
    e = v.numerator.bit_length() - v.denominator.bit_length()
    if Fraction(2) ** e > v: e -= 1
    elif Fraction(2) ** (e + 1) <= v: e += 1
    mant = v / Fraction(2) ** (e - fbits) - (1 << fbits); assert mant.denominator == 1 and 0 <= mant.numerator < (1 << fbits), (v, e)
    return (s << (width - 1)) | ((e + bias) << fbits) | mant.numerator
def rnd(a, q, s, mode):
    """round non-negative Fraction a to a multiple of 2^q in mode (s = sign of the value)"""
    scaled = a / Fraction(2) ** q
    m = scaled.numerator // scaled.denominator; rem = scaled - m
    if rem == 0: return a, False
    half = Fraction(1, 2)
    if mode == 0: inc = rem > half or (rem == half and (m & 1))
    elif mode == 4: inc = rem >= half
    elif mode == 1: inc = False
    elif mode == 2: inc = not s
    else: inc = bool(s)
    return (m + inc) * Fraction(2) ** q, True
def expected(fr, mode):
    """fr: exact (or 256-bit) signed Fraction of the true result -> (bits, flags)"""
    s = 1 if fr < 0 else 0; a = abs(fr)
    if a == 0: return encode(Fraction(0), s), 0
    e = a.numerator.bit_length() - a.denominator.bit_length()
    if Fraction(2) ** e > a: e -= 1
    elif Fraction(2) ** (e + 1) <= a: e += 1
    q_unb = e - (p - 1)
    vu, _ = rnd(a, q_unb, s, mode)
    tiny = vu < Fraction(2) ** emin
    q = max(q_unb, emin - (p - 1))
    v, inexact = rnd(a, q, s, mode)
    if v >= Fraction(2) ** (emax + 1):
        maxf = (Fraction(2) - Fraction(2) ** (1 - p)) * Fraction(2) ** emax
        to_inf = mode in (0, 4) or (mode == 2 and not s) or (mode == 3 and s)
        if to_inf: return (s << (width - 1)) | (((1 << (width - fbits - 1)) - 1) << fbits), OVF | INX
        return encode(maxf, s), OVF | INX
    fl = INX if inexact else 0
    if inexact and tiny: fl |= UNF
    return encode(v, s), fl
def mpf_to_frac(v):
    sign, man, exp, bc = v._mpf_
    if man == 0:
        if exp == 0 and bc == 0 and v == 0: return Fraction(0)
        return None
    fr = Fraction(man) * Fraction(2) ** exp
    return -fr if sign else fr
def is_pow2(fr):
    return fr > 0 and fr.numerator & (fr.numerator - 1) == 0 and fr.denominator & (fr.denominator - 1) == 0
def pow2_exp(fr):
    return fr.numerator.bit_length() - 1 - (fr.denominator.bit_length() - 1)
def true_value(op, x, y=None):
    """returns (fr, exact, side): fr = exact Fraction when exact, else a 320-bit approximation;
    side = +1/-1 when the true value is known to lie just above/below fr (fr representable), else 0.
    Returns None when the oracle cannot decide."""
    X = mp.mpf(x.numerator) / mp.mpf(x.denominator)
    if op in ('sinpi', 'cospi'):
        v = mpf_to_frac(mp.sinpi(X) if op == 'sinpi' else mp.cospi(X))
        if v is None: return None
        if abs(v) == 1: return v, False, (-1 if v > 0 else 1)      # |true| < 1 for non-(half)integer dyadic x
        return v, False, 0
    if op == 'rsqrt':
        if is_pow2(x) and pow2_exp(x) % 2 == 0: return Fraction(2) ** (-(pow2_exp(x) // 2)), True, 0
        v = mpf_to_frac(1 / mp.sqrt(X)); return (v, False, 0) if v is not None else None
    if op == 'hypot':
        s2 = x * x + y * y
        rn, rd = math.isqrt(s2.numerator), math.isqrt(s2.denominator)
        if rn * rn == s2.numerator and rd * rd == s2.denominator: return Fraction(rn, rd), True, 0
        Y = mp.mpf(y.numerator) / mp.mpf(y.denominator); v = mpf_to_frac(mp.sqrt(X * X + Y * Y))
        if v is None: return None
        if v == max(abs(x), abs(y)): return v, False, 1                  # strictly above the larger magnitude
        return v, False, 0
    if op == 'exp2':
        if x.denominator == 1: return Fraction(2) ** x.numerator, True, 0
        v = mpf_to_frac(mp.power(2, X))
        if v is None: return None
        if v == 1: return v, False, (1 if x > 0 else -1)
        return v, False, 0
    if op == 'exp2m1':
        if x.denominator == 1: return Fraction(2) ** x.numerator - 1, True, 0
        v = mpf_to_frac(mp.expm1(X * mp.log(2)))
        if v is None: return None
        if v == -1: return v, False, 1                                    # -1 + 2^x: above -1
        if v == 0: return None
        return v, False, 0
    if op == 'log2':
        if is_pow2(x): return Fraction(pow2_exp(x)), True, 0
        v = mpf_to_frac(mp.log(X, 2)); return (v, False, 0) if v is not None else None
    if op == 'log2p1':
        w = 1 + x
        if is_pow2(w): return Fraction(pow2_exp(w)), True, 0
        v = mpf_to_frac(mp.log1p(X) / mp.log(2)); return (v, False, 0) if v is not None else None
    return None
def exact_or_round(tv, mode):
    if tv is None: return None
    fr, exact, side = tv
    if exact: return expected(fr, mode)
    if side:
        fr = fr + side * abs(fr) * Fraction(2) ** -400
    else:
        # an inexact true value whose 320-bit approximation is exactly representable: undecidable here
        b, f = expected(fr, 0)
        if f == 0 and fr != 0: return None
    return expected(fr, mode)
OPS = ['sinpi', 'cospi', 'rsqrt', 'hypot', 'exp2', 'exp2m1', 'log2', 'log2p1']
def rand_bits():
    u = random.getrandbits(width)
    if random.random() < 0.5:
        emaxf = (1 << (width - fbits - 1)) - 1
        e = random.randint(0, emaxf - 1)
        u = (u & ~(((1 << (width - fbits - 1)) - 1) << fbits)) | (e << fbits)
    return u
def gen_input(op):
    """return (a_bits, b_bits or None) with finite, in-domain, non-trivial inputs"""
    while True:
        if op == 'hypot':
            a, b = rand_bits(), rand_bits()
            if random.random() < 0.3:  # close exponents
                b = (b & ~(((1 << (width - fbits - 1)) - 1) << fbits)) | ((((a >> fbits) & ((1 << (width - fbits - 1)) - 1)) + random.randint(-3, 3)) % ((1 << (width - fbits - 1)) - 1)) << fbits
            if random.random() < 0.05:  # scaled 3-4-5 triple (exact)
                k = random.randint(emin + 3, emax - 3); a = encode(3 * Fraction(2) ** k, 0); b = encode(4 * Fraction(2) ** k, 0)
            xa, xb = decode(a), decode(b)
            if xa is None or xb is None: continue
            return a, b
        a = rand_bits(); x = decode(a)
        if x is None: continue
        r = random.random()
        if op in ('sinpi', 'cospi'):
            if r < 0.15:  # near integers / half-integers: n/2 +- k ulp
                n = random.randint(-2000, 2000); base = Fraction(n, 2)
                if base == 0: continue
                bb = encode(abs(base), 0) | ((1 if base < 0 else 0) << (width - 1))
                a = bb + random.randint(-3, 3) if (bb & ((1 << (width - 1)) - 1)) > 3 else bb
                x = decode(a)
                if x is None or x == 0: continue
            if abs(x) >= Fraction(2) ** (p - 1) or x == 0: continue
            if (x * 2).denominator == 1: continue   # exact integer/half-integer handled by specials elsewhere
            return a, None
        if op == 'rsqrt':
            if x <= 0: continue
            if r < 0.05: x4 = Fraction(4) ** random.randint(emin // 2 + 2, emax // 2 - 2); a = encode(x4, 0)
            return a, None
        if op in ('exp2', 'exp2m1'):
            if r < 0.3: # integers and near-integers
                n = random.randint(emin - p - 2, emax + 2); bb = encode(Fraction(abs(n)), 0) | ((1 if n < 0 else 0) << (width - 1)) if n != 0 else 0
                a = bb + random.choice([0, 0, 1, -1, 2, -2]); x = decode(a)
                if x is None or x == 0: continue
            if r >= 0.3 and r < 0.5:  # tiny
                a = a & ((1 << (width - 1)) | ((1 << (fbits + 4)) - 1)); x = decode(a)
                if x == 0: continue
            if x == 0: continue
            if abs(x) > 2 * (emax + p + 10): continue  # saturated regions: trivially inf/0/-1 - keep a few
            return a, None
        if op == 'log2':
            if x <= 0: continue
            if r < 0.2:  # near 1
                one = encode(Fraction(1), 0); a = one + random.randint(-40, 40); x = decode(a)
            if r >= 0.2 and r < 0.3: a = encode(Fraction(2) ** random.randint(emin - fbits, emax), 0); x = decode(a)
            if x <= 0: continue
            return a, None
        if op == 'log2p1':
            if x <= -1: continue
            if r < 0.2:  # near 0 and near -1
                a = a & ((1 << (width - 1)) | ((1 << (fbits + 8)) - 1)); x = decode(a)
            if r >= 0.2 and r < 0.3: # x = 2^k - 1 (exact) +- ulp
                k = random.randint(1, p); a = encode(Fraction(2) ** k - 1, 0) + random.choice([0, 0, 1, -1]); x = decode(a)
            if r >= 0.3 and r < 0.4: # near -1
                mo = encode(Fraction(1), 1); a = mo - random.randint(1, 60); x = decode(a)
            if x is None or x <= -1 or x == 0: continue
            return a, None
cases = []
if EXH:
    for op in [o for o in OPS if o != 'hypot']:
        for u in range(1 << width):
            x = decode(u)
            if x is None: continue
            if op in ('sinpi', 'cospi') and (x == 0 or (x * 2).denominator == 1): continue
            if op == 'rsqrt' and x <= 0: continue
            if op in ('exp2', 'exp2m1') and x == 0: continue
            if op == 'log2' and x <= 0: continue
            if op == 'log2p1' and (x <= -1 or x == 0): continue
            for m in MODES: cases.append((op, m, u, None))
else:
    for op in OPS:
        for _ in range(N):
            a, b = gen_input(op)
            for m in MODES: cases.append((op, m, a, b))
inp = ''.join(f"{FMT} {op} {m} {a:x}" + (f" {b:x}" if b is not None else "") + "\n" for op, m, a, b in cases)
out = subprocess.run([DRIVER], input=inp, capture_output=True, text=True).stdout.splitlines()
assert len(out) == len(cases), (len(out), len(cases))
bad = {o: 0 for o in OPS}; n = {o: 0 for o in OPS}; shown = 0; cache = {}; undecided = 0
for (op, m, a, b), o in zip(cases, out):
    r_s, f_s = o.split(); r = int(r_s, 16); f = int(f_s, 16)
    key = (op, a, b)
    if key not in cache:
        x = decode(a); y = decode(b) if b is not None else None
        cache[key] = true_value(op, x, y)
    tv = cache[key]
    exp = exact_or_round(tv, m)
    if exp is None: undecided += 1; continue
    eb, ef = exp
    n[op] += 1
    if not (r == eb and f == ef):
        bad[op] += 1
        if shown < 30:
            print(f"  MISMATCH f{FMT} {op} rm={m} a={a:x}" + (f" b={b:x}" if b is not None else "") + f" msf={r:x}/{f:02x} expected={eb:x}/{ef:02x}"); shown += 1
print(f"mathdiff f{FMT} {'EXHAUSTIVE' if EXH else 'N=' + str(N) + '/op'} x 5 modes: " + ' '.join(f"{o}={bad[o]}/{n[o]}" for o in OPS) + f" -> total mismatches {sum(bad.values())} of {sum(n.values())} (oracle-undecided skipped: {undecided})")
