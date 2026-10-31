import random, subprocess, sys, struct, math
from fractions import Fraction
from decimal import Decimal, getcontext
getcontext().prec = 1200
DRIVER = sys.argv[1]; N = int(sys.argv[2]); random.seed(20261031)
INV, DBZ, OVF, UNF, INX = 1, 2, 4, 8, 16
def bits(x): return struct.unpack('<Q', struct.pack('<d', x))[0]
def ofbits(u): return struct.unpack('<d', struct.pack('<Q', u))[0]
def round53_unbounded(fr):
    """nearest-even rounding of a positive Fraction to 53 significant bits, unbounded exponent; returns Fraction"""
    if fr == 0: return fr
    n, d = fr.numerator, fr.denominator
    e = n.bit_length() - d.bit_length()
    # find e with 2^e <= fr < 2^(e+1)
    if Fraction(2)**e > fr: e -= 1
    elif Fraction(2)**(e+1) <= fr: e += 1
    scale = Fraction(2)**(52 - e)
    q = fr * scale
    m = q.numerator // q.denominator
    rem = q - m
    if rem > Fraction(1,2) or (rem == Fraction(1,2) and (m & 1)): m += 1
    return Fraction(m) / scale
MINNORM = Fraction(2)**-1022
def expected_flags_from(fr_abs, result):
    """flags expected for decimal/hex -> binary64 (te) given exact |value| and the delivered result"""
    if math.isinf(result): return OVF | INX
    rf = Fraction(result) if result == result else None
    inexact = (rf is None) or (abs(rf) != fr_abs)
    fl = INX if inexact else 0
    if inexact and fr_abs != 0:
        if round53_unbounded(fr_abs) < MINNORM: fl |= UNF
    return fl
def gen_decimal():
    k = random.random()
    if k < 0.35:
        nd = random.randint(1, 20); digits = ''.join(random.choice('0123456789') for _ in range(nd))
        if digits[0] == '0': digits = str(random.randint(1,9)) + digits[1:]
        exp = random.randint(-330, 310) - nd
        return f"{random.choice(['','-'])}{digits}e{exp}"
    if k < 0.75:
        # near a binary64 midpoint: midpoint between d and next, written to 17..20 sig digits
        while True:
            u = random.getrandbits(64) & 0x7fefffffffffffff
            if (u >> 52) == 0x7ff: continue
            d = ofbits(u)
            if d == 0: continue
            nxt = ofbits(u + 1)
            if math.isinf(nxt): continue
            mid = (Fraction(d) + Fraction(nxt)) / 2
            nd = random.randint(17, 20)
            dec = Decimal(mid.numerator) / Decimal(mid.denominator)
            s = f"{dec:.{nd-1}e}"
            return random.choice(['','-']) + s
    if k < 0.9:
        # subnormal / tiny region, 15-20 digits
        nd = random.randint(15, 20); digits = str(random.randint(1,9)) + ''.join(random.choice('0123456789') for _ in range(nd-1))
        exp = random.randint(-324, -300) - nd + 1
        return f"{digits}e{exp}"
    # fixed notation with a point
    ip = str(random.randint(0, 10**random.randint(1,10))); fp = ''.join(random.choice('0123456789') for _ in range(random.randint(1,12)))
    return f"{random.choice(['','-'])}{ip}.{fp}"
def gen_hex():
    nd = random.randint(1, 30); digs = ''.join(random.choice('0123456789abcdef') for _ in range(nd))
    lead = random.choice(['0','1','1','f','a'])
    exp = random.randint(-1120, 1030)
    return f"{random.choice(['','-'])}0x{lead}.{digs}p{exp}"
cases = []
for _ in range(N): cases.append(('D', gen_decimal()))
for _ in range(N): cases.append(('H', gen_hex()))
tod = []
for _ in range(N):
    u = random.getrandbits(64)
    if random.random() < 0.3: u = (u & 0x800fffffffffffff) | (random.randint(0, 2046) << 52)
    p = random.randint(1, 20)
    tod.append((u, p))
for u, p in tod: cases.append(('T', f"{u:016x} {p}"))
for u, p in tod: cases.append(('X', f"{u:016x}"))
inp = ''.join(f"{c[0]} {c[1]}\n" for c in cases)
out = subprocess.run([DRIVER], input=inp, capture_output=True, text=True).stdout.splitlines()
assert len(out) == len(cases), (len(out), len(cases))
bad = {'D':0,'H':0,'T':0,'X':0}; shown = 0
def show(msg):
    global shown
    if shown < 25: print("  MISMATCH", msg); shown += 1
for (kind, arg), o in zip(cases, out):
    if kind in 'DH':
        bits_s, fl_s, cons_s = o.split(); r = int(bits_s, 16); fl = int(fl_s, 16); cons = int(cons_s)
        if kind == 'D':
            py = float(arg); fr = abs(Fraction(arg))  # Fraction accepts decimal strings exactly
        else:
            try: py = float.fromhex(arg)
            except OverflowError: py = float('-inf') if arg.startswith('-') else float('inf')
            # exact value of the hex string
            s = arg.lstrip('-'); mant, _, ex = s[2:].partition('p'); ip, _, fp = mant.partition('.')
            fr = Fraction(int(ip + fp, 16), 16**len(fp)) * Fraction(2)**int(ex)
        exp_bits = bits(py)
        exp_fl = expected_flags_from(fr, py)
        ok = (r == exp_bits) and (fl == exp_fl) and (cons == len(arg))
        if not ok:
            bad[kind] += 1; show(f"{kind} {arg[:80]} -> msf {bits_s}/{fl_s}/{cons} expected {exp_bits:016x}/{exp_fl:02x}/{len(arg)}")
    elif kind == 'T':
        u_s, p_s = arg.split(); u = int(u_s, 16); p = int(p_s); x = ofbits(u)
        s, fl_s, n_s = o.split('|'); fl = int(fl_s, 16)
        if x != x:
            ok = s == (('-' if u >> 63 else '') + ('nan' if (u >> 51) & 1 else 'snan'))
            exp_fl = 0
        elif math.isinf(x):
            ok = s == ('-inf' if x < 0 else 'inf'); exp_fl = 0
        else:
            exp = f"{x:.{p-1}e}"
            ok = (s == exp)
            exp_fl = 0 if Fraction(Decimal(s)) == Fraction(x) else INX
        if not (ok and fl == exp_fl and int(n_s) == len(s)):
            bad['T'] += 1; show(f"T {u_s} p={p} -> msf '{s}'/{fl_s}/{n_s} expected '{exp if not (x!=x or math.isinf(x)) else '(special)'}'/{exp_fl:02x}")
    else:
        u = int(arg, 16); x = ofbits(u); s, fl_s, n_s = o.split('|')
        if x != x: ok = s == (('-' if u >> 63 else '') + ('nan' if (u >> 51) & 1 else 'snan'))
        elif math.isinf(x): ok = s == ('-inf' if x < 0 else 'inf')
        else:
            try: ok = (float.fromhex(s) == x) and (math.copysign(1, float.fromhex(s)) == math.copysign(1, x)) and fl_s == '00'
            except ValueError: ok = False
        if not (ok and int(n_s) == len(s)):
            bad['X'] += 1; show(f"X {arg} -> msf '{s}'/{fl_s}/{n_s} python {x.hex()}")
print(f"strdiff: N={N} per kind; mismatches from-decimal={bad['D']} from-hex={bad['H']} to-decimal(1..20 digits)={bad['T']} to-hex-exact={bad['X']}")
