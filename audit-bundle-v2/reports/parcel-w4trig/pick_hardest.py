"""Pick measured-hardest input patterns for committed vectors.

f64: margin over the spike's MPFR-redecided wide values
(parsed exactly as Fractions from hex) - genuine families by
-log2(dist to boundary / ulp), saturation split as in spike.
f32: fresh mpmath margin scan over directed candidate sets
(pi-convergent neighbourhoods + lattice + seeded).
Prints Python literals for gen_vectors_trig.py HARDEST_EXT.
Inputs only are selected; values are never used.
"""
import math
import random
from fractions import Fraction

import mpmath


def parse_hexfrac(s):
    neg = s.startswith("-")
    s = s.lstrip("+-")
    assert s.startswith("0x"), s[:12]
    mant, _, ex = s[2:].partition("p")
    ip, _, fp = mant.partition(".")
    num = int(ip + fp, 16)
    den = 16 ** len(fp)
    v = Fraction(num, den) * Fraction(2) ** int(ex)
    return -v if neg else v


def ulp_of(v, p=53, emin=-1022):
    if v == 0:
        return Fraction(2) ** (emin - (p - 1))
    e = math.floor(mpmath.log(abs(float(v)), 2)) if abs(v) > Fraction(2) ** -1000 else emin
    # exact binade:
    a = abs(v)
    e = a.numerator.bit_length() - a.denominator.bit_length()
    while Fraction(2) ** e > a:
        e -= 1
    while Fraction(2) ** (e + 1) <= a:
        e += 1
    e = max(e, emin)
    return Fraction(2) ** (e - (p - 1))


def margin_bits(v, p, emin):
    """extra bits = -log2(min dist to midpoint or representable / ulp)"""
    if v == 0:
        return -1.0
    u = ulp_of(v, p, emin)
    k = v / u
    fl = math.floor(k)
    frac = k - fl
    d_rep = min(frac, 1 - frac)
    d_mid = abs(frac - Fraction(1, 2))
    d = min(d_rep, d_mid)
    if d == 0:
        return 999.0
    return -math.log2(float(d))


def pick_f64(fn, n_gen=110, n_sat=18):
    rows = []
    with open(f"scratch/tier2-trig-spike/out/wc_{fn}_redecided.txt") as fh:
        for line in fh:
            t = line.split()
            if len(t) != 6 or t[1] in ("NONFINITE", "+0x0p+0", "-0x0p+0"):
                continue
            v = parse_hexfrac(t[1])
            m = margin_bits(v, 53, -1022)
            u1 = ulp_of(v, 53, -1022)
            sat = abs(abs(v) - 1) <= 2 * u1
            rows.append((m, t[0], sat))
    gen = sorted([r for r in rows if not r[2]], reverse=True)[:n_gen]
    sat = sorted([r for r in rows if r[2]], reverse=True)[:n_sat]
    pats = [f"0x{r[1].upper()}" for r in gen + sat]
    print(f"# f64 {fn}: {len(rows)} rows, top genuine margin {gen[0][0]:.2f}")
    return pats


def f32_candidates():
    cand = set()
    rng = random.Random(777)
    # pi-convergent neighbourhoods: r near j/113, j/355-approx
    for j in range(1, 400):
        for den in (7, 113, 355, 1068):
            cand.add(Fraction(j, den) if j < den else Fraction(j % den, den))
    for k in range(-149, 30, 7):
        for m in (1, 3, 5, 9, 113, 355, 12345):
            cand.add(Fraction(m) * Fraction(2) ** k)
    while len(cand) < 6000:
        cand.add(Fraction(rng.getrandbits(24)) * Fraction(2) ** rng.randint(-40, 5))
    return cand


def enc32(v):
    import struct
    try:
        f = float(v)
    except OverflowError:
        return None
    b = struct.unpack("<I", struct.pack("<f", f))[0]
    # ensure the f32 exactly equals v (dyadic candidates mostly)
    back = Fraction(struct.unpack("<f", struct.pack("<I", b))[0])
    if back != v:
        v = back  # margin computed on the true encoding value
    return b, v


def pick_f32(n=64):
    mpmath.mp.dps = 45
    res = {"sin_pi": [], "cos_pi": []}
    seen = set()
    for v in f32_candidates():
        got = enc32(v)
        if got is None:
            continue
        b, val = got
        if b in seen or val == 0 or abs(val) >= 2:
            continue
        seen.add(b)
        x = mpmath.mpf(val.numerator) / val.denominator
        for fn, fun in (("sin_pi", mpmath.sinpi), ("cos_pi", mpmath.cospi)):
            y = fun(x)
            yf = Fraction(y._mpf_[1]) * Fraction(2) ** y._mpf_[2]
            if y._mpf_[0]:
                yf = -yf
            m = margin_bits(yf, 24, -126)
            res[fn].append((m, b))
    out = {}
    for fn in res:
        top = sorted(set(res[fn]), reverse=True)[:n]
        out[fn] = [f"0x{b:08X}" for _, b in top]
        print(f"# f32 {fn}: top margin {top[0][0]:.2f} min {top[-1][0]:.2f}")
    return out


print("HARDEST_EXT = {")
s = pick_f64("sinpi")
c = pick_f64("cospi")
print('    "f64": {')
print('        "sin_pi": [' + ", ".join(s) + "],")
print('        "cos_pi": [' + ", ".join(c) + "],")
print("    },")
f32 = pick_f32()
print('    "f32": {')
print('        "sin_pi": [' + ", ".join(f32["sin_pi"]) + "],")
print('        "cos_pi": [' + ", ".join(f32["cos_pi"]) + "],")
print("    },")
print('    "f16": {"sin_pi": [], "cos_pi": []},')
print("}")
