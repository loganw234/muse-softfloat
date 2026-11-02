"""Build the cross-decision sample set (own code, own RNG).

- specials: zeros/infs/NaN payloads, small integers/half-integers,
  large integers/half-integers across binades incl. max-finite.
- seeded strata per format/function: uniform finite, near-integer,
  near-half, near-quarter bounces, tiny (exp >= -70, mpmath-feasible).
- hardest: mechanical parse of the pinned .wc files (strip '#'
  comments, first whitespace token, float.fromhex to bits; classify
  finite/NaN/inf/unparsed), margin-ranked at dps 60 (own measurement),
  top 50 per function + 500 uniform random from each file.
Writes one INFILE (op hex per line) for both deciders.
"""
import math
import os
import random
import struct
import sys
from fractions import Fraction

import mpmath

ROOT = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
OR = os.path.join(ROOT, "scratch", "oracles",
                  "core-math-3b2163bb87c222c7db17a721425fbef31e98fd94",
                  "src", "binary64")
FMTS = {"msf16": (16, 5), "msf32": (32, 8), "msf64": (64, 11)}
FNS = ("sin_pi", "cos_pi")


def params(fmt):
    bits, w = FMTS[fmt]
    t = bits - 1 - w
    return {"bits": bits, "t": t, "bias": (1 << (w - 1)) - 1,
            "emaxf": (1 << w) - 1, "sign": 1 << (bits - 1)}


def finite_bits(fmt):
    q = params(fmt)
    while True:
        x = random.getrandbits(q["bits"])
        if ((x >> q["t"]) & q["emaxf"]) != q["emaxf"]:
            return x


def encode_int(fmt, n):
    """Exact encoding of integer n (any sign) or None if not exact."""
    q = params(fmt)
    if n == 0:
        return 0
    sign = 1 if n < 0 else 0
    a = abs(n)
    e = a.bit_length() - 1
    t = q["t"]
    if e - t > q["bias"]:
        return None
    if e >= t:
        if a & ((1 << (e - t)) - 1):
            return None
        ef = e - (q["bias"] - 0) + q["bias"]
        ef = e + q["bias"]
        frac = (a >> (e - t)) & ((1 << t) - 1)
    else:
        ef = 0
        frac = a << (t - e)
        if ef == 0 and frac >= (1 << t):
            return None
    if ef >= q["emaxf"]:
        return None
    return (sign << (q["bits"] - 1)) | (ef << t) | (frac & ((1 << t) - 1))


def specials(fmt):
    q = params(fmt)
    inf = q["emaxf"] << q["t"]
    out = {0, q["sign"], inf, inf | q["sign"]}
    # NaN payload samples
    t = q["t"]
    out.add((q["emaxf"] << t) | (1 << (t - 1)) | 0x1234 % (1 << (t - 1)))
    out.add((q["emaxf"] << t) | (1 << (t - 1)) | ((1 << (t - 1)) - 1))
    out.add((q["emaxf"] << t) | (0x35 % (1 << (t - 1)) or 1))
    out.add((q["sign"]) | (q["emaxf"] << t) | (1 << (t - 1)) | 0x5)
    for n in range(-10, 11):
        e = encode_int(fmt, n)
        if e is not None:
            out.add(e)
    for n in range(-10, 10):
        for sgn in (1, -1):
            v = Fraction(sgn * (2 * abs(n) + 1), 2)
            e = encode_frac(fmt, v)
            if e is not None:
                out.add(e)
    # large integers / half-integers across binades + max finite
    for k in (24, 25, 52, 53, 100, 500, 1000):
        for sgn in (1, -1):
            for dv in (0, Fraction(1, 2)):
                e = encode_frac(fmt, Fraction(sgn * 2 ** k) + dv)
                if e is not None:
                    out.add(e)
    maxf = ((q["emaxf"] - 1) << t) | ((1 << t) - 1)
    out.add(maxf)
    out.add(maxf | q["sign"])
    return sorted(out)


def encode_frac(fmt, v):
    q = params(fmt)
    if v == 0:
        return 0
    sign = 1 if v < 0 else 0
    av = abs(v)
    num, den = av.numerator, av.denominator
    if den & (den - 1):
        return None
    d2 = den.bit_length() - 1
    e = num.bit_length() - 1 - d2
    t = q["t"]
    if e > q["bias"]:
        return None
    if e >= 1 - q["bias"]:
        ef = e + q["bias"]
        nb = num.bit_length() - 1
        if nb > t:
            if num & ((1 << (nb - t)) - 1):
                return None
            full = num >> (nb - t)
        else:
            full = num << (t - nb)
        frac = full & ((1 << t) - 1)
        if ef >= q["emaxf"]:
            return None
        return (sign << (q["bits"] - 1)) | (ef << t) | frac
    else:
        # subnormal
        emin = 1 - q["bias"]
        k = av / Fraction(2) ** (emin - t)
        if k.denominator != 1 or k >= 1 << t or k <= 0:
            return None
        return (sign << (q["bits"] - 1)) | int(k)


def ulp_bits(fmt, x):
    q = params(fmt)
    t = q["t"]
    e = (x >> t) & q["emaxf"]
    if e == 0:
        return 1
    return 1 << max(0, (e - q["bias"]) - t + t - t)


def neighbours(fmt, x, n=3):
    q = params(fmt)
    mod = 1 << q["bits"]
    out = set()
    for d in range(-n, n + 1):
        y = (x + d) % mod
        if ((y >> q["t"]) & q["emaxf"]) != q["emaxf"]:
            out.add(y)
    return out


def seeded(fmt, fn, n, rng):
    q = params(fmt)
    out = set()
    while len([v for v in out]) < n:
        r = rng.random()
        if r < 0.45:
            out.add(finite_bits(fmt))
        elif r < 0.60:
            # near-integer bounce
            k = rng.choice([1, 2, 3, 7, 100, 1000, 2 ** 20, 2 ** 40])
            sgn = rng.choice([1, -1])
            base = encode_frac(fmt, Fraction(sgn * k))
            if base is None:
                continue
            out.update(neighbours(fmt, base, 3))
        elif r < 0.75:
            k = rng.choice([0, 1, 2, 5, 50, 500, 2 ** 19])
            sgn = rng.choice([1, -1])
            base = encode_frac(fmt, Fraction(sgn * k) + Fraction(1, 2))
            if base is None:
                continue
            out.update(neighbours(fmt, base, 3))
        elif r < 0.85:
            k = rng.choice([0, 1, 3, 9])
            sgn = rng.choice([1, -1])
            base = encode_frac(fmt, Fraction(sgn * k) + Fraction(1, 4))
            if base is None:
                continue
            out.update(neighbours(fmt, base, 2))
        else:
            # tiny but mpmath-feasible (binary exp >= -70)
            e = rng.randint(-70, -1)
            mant = rng.getrandbits(min(q["t"] + 1, 24))
            v = Fraction(mant, 1) * Fraction(2) ** (e - 24)
            sgn = rng.choice([1, -1])
            be = encode_frac(fmt, sgn * v)
            if be is not None and ((be >> q["t"]) & q["emaxf"]) \
                    != q["emaxf"]:
                out.add(be)
    return sorted(out)[:n]


def parse_wc(path):
    toks = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.split("#", 1)[0].split()
            if not s:
                continue
            if len(s) != 1:
                raise AssertionError(f"multi-token data line in {path}")
            toks.append(s[0])
    n_fin = n_nan = n_inf = n_unp = 0
    fin = []
    for tok in toks:
        try:
            d = float.fromhex(tok)
        except ValueError:
            n_unp += 1
            continue
        if math.isnan(d):
            n_nan += 1
        elif math.isinf(d):
            n_inf += 1
        else:
            n_fin += 1
            fin.append(struct.unpack("<Q", struct.pack("<d", d))[0])
    return toks, fin, (n_fin, n_nan, n_inf, n_unp)


def margin_rank(sample_bits, fn, dps=60):
    """Own extra-bits measurement at modest precision (ranking only)."""
    mpmath.mp.dps = dps
    out = []
    for b in sample_bits:
        d = struct.unpack("<d", struct.pack("<Q", b))[0]
        if d == 0.0 or math.isinf(d) or math.isnan(d):
            continue
        x = mpmath.mpf(d)
        y = mpmath.cospi(x) if fn == "cos_pi" else mpmath.sinpi(x)
        if y == 0:
            continue
        ay = abs(y)
        # distance to nearest representable/midpoint at f64
        m, e = math.frexp(float(ay)) if ay < 1e308 else (0.0, 0)
        ulp = math.ldexp(1.0, e - 53)
        f = float(ay)
        lo = math.floor(f / ulp) * ulp if ulp > 0 else f
        d_rep = min(abs(f - lo), abs(f - (lo + ulp)))
        d_mid_points = sorted([abs(f - lo), abs(f - (lo + ulp)),
                               abs(f - (lo + ulp / 2))])
        extra = -math.log2(max(d_mid_points[0], 1e-320) / ulp) \
            if ulp > 0 else 0.0
        out.append((extra, b))
    out.sort(reverse=True)
    return out


def main():
    dest = sys.argv[1]
    rng = random.Random(999)
    jobs = []
    for fmt in FMTS:
        for x in specials(fmt):
            for fn in FNS:
                jobs.append((fn, fmt, x))
    for fmt in FMTS:
        for fn in FNS:
            for x in seeded(fmt, fn, 3000, rng):
                jobs.append((fn, fmt, x))
    # hardest: parse + rank + top/random
    for fn, name in (("sin_pi", "sinpi"), ("cos_pi", "cospi")):
        path = os.path.join(OR, name, name + ".wc")
        toks, fin, counts = parse_wc(path)
        print(f"{name}.wc tokens={len(toks)} "
              f"finite={counts[0]} nan={counts[1]} inf={counts[2]} "
              f"unparsed={counts[3]} unique_finite={len(set(fin))}")
        ranked = margin_rank(random.Random(7).sample(
            fin, min(4000, len(fin))), fn)
        ranked.sort(reverse=True)
        top = [b for _, b in ranked[:50]]
        rnd = random.Random(11).sample(sorted(set(fin)),
                                       min(500, len(set(fin))))
        for x in top + rnd:
            jobs.append((fn, "msf64", x))
    seen = set()
    with open(dest, "w") as fh:
        for fn, fmt, x in jobs:
            key = (fmt, fn, x)
            if key in seen:
                continue
            seen.add(key)
            fh.write(f"{fmt}_{fn} {x:x}\n")
    print(f"wrote {dest}: {len(seen)} inputs")


main()
