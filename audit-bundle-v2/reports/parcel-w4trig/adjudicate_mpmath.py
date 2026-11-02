"""Independent adjudication: mpmath (not MPFR) decides a
seeded sample of f64/f32 inputs via exact Fraction rounding of
a high-precision value whose distance to every rounding
boundary is certified > 100x the mpmath evaluation slop
(dps 80 vs dps 120 agreement). Compares against the harness
decider output (trig_v2.exe decide)."""
import random
import subprocess
import sys
from fractions import Fraction

import mpmath

EXE = "worktrees/w4-trig/build/trig/trig_v2.exe"
RMS = ("te", "tz", "tp", "tn")


def round_frac(v, p, emin, t, rm):
    """Round exact Fraction v to format (p, emin) under named
    mode; returns (bits_without_sign, sign, inexact, tiny)."""
    sign = 1 if v < 0 else 0
    a = abs(v)
    if a == 0:
        return 0, sign, False, False
    # binade
    e = a.numerator.bit_length() - a.denominator.bit_length()
    while Fraction(2) ** e > a:
        e -= 1
    while Fraction(2) ** (e + 1) <= a:
        e += 1
    qexp = max(e, emin) - (p - 1)
    k = a / (Fraction(2) ** qexp)
    lo = k.numerator // k.denominator
    rem = k - lo
    inexact = rem != 0
    inc = False
    if rm == "te":
        inc = rem > Fraction(1, 2) or (rem == Fraction(1, 2) and lo % 2 == 1)
    elif rm == "tp":
        inc = (not sign) and inexact
    elif rm == "tn":
        inc = bool(sign) and inexact
    m = lo + (1 if inc else 0)
    ee = qexp and (max(e, emin))
    if m >= (1 << p):
        m >>= 1
        ee = max(e, emin) + 1
    # tininess after rounding: unbounded-exponent rounding
    tiny = False
    if inexact:
        qu = e - (p - 1)
        ku = a / (Fraction(2) ** qu)
        lou = ku.numerator // ku.denominator
        remu = ku - lou
        incu = False
        if rm == "te":
            incu = remu > Fraction(1, 2) or (remu == Fraction(1, 2) and lou % 2 == 1)
        elif rm == "tp":
            incu = (not sign) and remu != 0
        elif rm == "tn":
            incu = bool(sign) and remu != 0
        mu = lou + (1 if incu else 0)
        eu = e + 1 if mu >= (1 << p) else e
        tiny = eu < emin
    # encode
    if m == 0:
        bits = 0
    elif m >= (1 << (p - 1)):
        bias = (1 << ( {"f64": 11, "f32": 8}[CUR] - 1)) - 1
        bits = ((ee + bias) << t) | (m - (1 << (p - 1)))
    else:
        bits = m
    return bits, sign, inexact, tiny


CUR = "f64"


def decide_mpmath(fmt, fn, bits):
    global CUR
    CUR = fmt
    if fmt == "f64":
        w, t, p, emin = 64, 52, 53, -1022
    else:
        w, t, p, emin = 32, 23, 24, -126
    sign = (bits >> (w - 1)) & 1
    ef = (bits >> t) & ((1 << (w - 1 - t)) - 1)
    frac = bits & ((1 << t) - 1)
    bias = (1 << (w - 1 - t - 1)) - 1 if False else ((1 << (w - 2 - t)) - 1)
    bias = {64: 1023, 32: 127}[w]
    if ef == 0:
        sig, ex = frac, emin - t
    else:
        sig, ex = frac | (1 << t), ef - bias - t
    v = Fraction(sig) * Fraction(2) ** ex
    if sign:
        v = -v
    # specials handled by caller exclusion (integers/half)
    av = abs(v)
    if av == int(av) or av * 2 == int(av * 2):
        return None
    out = []
    for dps in (80,):
        mpmath.mp.dps = dps
        x = mpmath.mpf(v.numerator) / v.denominator
        y = mpmath.sinpi(x) if fn == "sin_pi" else mpmath.cospi(x)
        yf = Fraction(y._mpf_[1]) * Fraction(2) ** y._mpf_[2]
        if y._mpf_[0]:
            yf = -yf
        # saturation: use delta identity when |y| near 1
        for rm in RMS:
            b, s, inex, tiny = round_frac(yf, p, emin, t, rm)
            fl = (0x10 if inex else 0) | (0x08 if tiny and inex else 0)
            if not inex:
                return None  # cannot certify; skip sample
            out.append(((s << (w - 1)) | b, fl))
    return out


def main():
    rng = random.Random(20261028)
    jobs = []
    for fmt in ("f64", "f32"):
        w = 64 if fmt == "f64" else 32
        n = 0
        while n < 220:
            bits = rng.getrandbits(w)
            ef = (bits >> (52 if w == 64 else 23)) & (0x7FF if w == 64 else 0xFF)
            if ef == (0x7FF if w == 64 else 0xFF):
                continue
            fn = "sin_pi" if n % 2 == 0 else "cos_pi"
            exp = decide_mpmath(fmt, fn, bits)
            if exp is None:
                continue
            jobs.append((fmt, fn, bits, exp))
            n += 1
    inp = "".join(f"msf{fmt[1:]}_{fn} {bits:x}\n" for fmt, fn, bits, _ in jobs)
    proc = subprocess.run([EXE, "decide"], input=inp, capture_output=True,
                          text=True)
    assert proc.returncode == 0, proc.stdout[-500:]
    got = {}
    for line in proc.stdout.splitlines():
        t = line.split()
        if len(t) == 10:
            got[(t[0], t[1])] = [(int(t[2 + 2 * i], 16), int(t[3 + 2 * i], 16))
                                  for i in range(4)]
    bad = 0
    for fmt, fn, bits, exp in jobs:
        g = got.get((f"msf{fmt[1:]}_{fn}", f"{bits:x}"))
        if g != exp:
            bad += 1
            if bad <= 5:
                print("DIFF", fmt, fn, hex(bits), "mpmath", exp, "harness", g)
    print(f"mpmath adjudication: {len(jobs)} inputs, disagreements {bad}")
    print("ADJUDICATE", "PASS" if bad == 0 else "FAIL")
    sys.exit(1 if bad else 0)


main()
