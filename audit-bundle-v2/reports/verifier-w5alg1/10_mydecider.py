#!/usr/bin/env python3
"""verifier-w5alg1 OWN exact integer decider for rSqrt.

Derived from scratch/sf2-algebraic/report.md Sec 3.1 (the study
definition), NOT from the copy's generator or C kernel:

  decode x = M * 2^E (M < 2^p); normalize by exact left shifts to
  M' in [2^(p-1), 2^p); if E' odd: M' *= 2, E' -= 1 (E' even).
  S = p + 9 + (p-1)//2; T = 2^(2S); Q = isqrt(T // M')  [exact:
  isqrt(floor(A)) == floor(sqrt(A))]; sticky = (Q*Q*M' != T).
  One rounding of (Q, sticky) at scale 2^(-S-E'/2) in the named
  mode decides bits+flags. Result range is strictly interior
  (no overflow/underflow/subnormal delivery possible); any such
  outcome aborts loudly instead of being averaged.

Specials from the study Sec 5.1 table (clause-extract basis):
  +0 -> +inf + divByZero; -0 -> -inf + divByZero (paired-sign
  cell; NEVER sourced from MPFR); +inf -> +0; -inf or negative
  finite -> default qNaN + invalid; qNaN -> itself; sNaN ->
  quieted + invalid. NaN payload/sign preserved per SF-0 matrix.

Different code path from the C kernel (bit search + split
compare) and from the copy generator (rational squaring):
direct isqrt on the full quotient + integer guard/round/sticky
rounding. Ties (midpoint exactly representable) are counted;
the study holds them unattainable for rSqrt.
"""
import sys
from math import isqrt

FMTS = {
    "f16": {"p": 11, "w": 5, "bias": 15},
    "f32": {"p": 24, "w": 8, "bias": 127},
    "f64": {"p": 53, "w": 11, "bias": 1023},
}
MODES = ("te", "tz", "tp", "tn", "ta")
INVALID = 0x01
DIVZERO = 0x02
INEXACT = 0x10

TIES_SEEN = []


def fmt_params(fmt):
    d = FMTS[fmt]
    p, w, bias = d["p"], d["w"], d["bias"]
    t = p - 1
    return {"p": p, "w": w, "t": t, "bias": bias,
            "emin": 1 - bias, "emax": bias,
            "emaxf": (1 << w) - 1,
            "qbit": 1 << (t - 1),
            "quiet": 1 << (t - 1)}


def classify(fmt, x):
    q = fmt_params(fmt)
    sign = (x >> (fmt_bits(fmt) - 1)) & 1
    ef = (x >> q["t"]) & q["emaxf"]
    frac = x & ((1 << q["t"]) - 1)
    if ef == q["emaxf"]:
        if frac == 0:
            return ("inf", sign)
        if frac & q["quiet"]:
            return ("qnan", sign, frac)
        return ("snan", sign, frac)
    if ef == 0 and frac == 0:
        return ("zero", sign)
    return ("num", sign, ef, frac)


def fmt_bits(fmt):
    return {"f16": 16, "f32": 32, "f64": 64}[fmt]


def default_qnan(fmt):
    q = fmt_params(fmt)
    return ((q["emaxf"] << q["t"]) | q["quiet"])


def inf_bits(fmt, sign):
    q = fmt_params(fmt)
    return (sign << (fmt_bits(fmt) - 1)) | (q["emaxf"] << q["t"])


def decide_special(fmt, x):
    """Table cells x5 modes, or None when regular."""
    q = fmt_params(fmt)
    c = classify(fmt, x)
    if c[0] == "qnan":
        return [(x, 0)] * 5
    if c[0] == "snan":
        return [(x | q["quiet"], INVALID)] * 5
    if c[0] == "zero":
        return [(inf_bits(fmt, c[1]), DIVZERO)] * 5
    if c[0] == "inf":
        if c[1] == 0:
            return [(0, 0)] * 5
        return [(default_qnan(fmt), INVALID)] * 5
    if c[0] == "num" and c[1] == 1:
        return [(default_qnan(fmt), INVALID)] * 5
    return None


def decide_finite(fmt, x):
    """Regular positive input -> [(bits, flags)] x5. All integer."""
    q = fmt_params(fmt)
    p, t, bias = q["p"], q["t"], q["bias"]
    c = classify(fmt, x)
    assert c[0] == "num" and c[1] == 0, (fmt, hex(x), c)
    _, _, ef, frac = c
    if ef == 0:
        m, e = frac, q["emin"] - t
    else:
        m, e = frac | (1 << t), ef - bias - t
    # Normalize: M' in [2^(p-1), 2^p), E' even, x = M' * 2^E'.
    mp = m
    ep = e
    while mp < (1 << (p - 1)):
        mp <<= 1
        ep -= 1
    if ep & 1:
        mp <<= 1
        ep -= 1
    assert (1 << (p - 1)) <= mp < (1 << (p + 1)), (fmt, hex(x), mp)
    assert ep % 2 == 0
    s = p + 9 + (p - 1) // 2
    qv = isqrt((1 << (2 * s)) // mp)
    sticky = (qv * qv * mp != (1 << (2 * s)))
    top = s - (p - 1) // 2
    assert qv <= (1 << top), (fmt, hex(x), qv, top)
    assert qv > (1 << (p + 7)), (fmt, hex(x), qv)
    bl = qv.bit_length()
    sh = bl - p
    kept = qv >> sh
    rem = qv - (kept << sh)
    g = (rem >> (sh - 1)) & 1
    r = (rem >> (sh - 2)) & 1
    low = rem & ((1 << (sh - 2)) - 1)
    st = sticky or (low != 0)
    exact = (rem == 0 and not sticky)
    e2 = (bl - 1) - s - ep // 2
    out = []
    for rm in MODES:
        if exact:
            cnd = kept
        elif rm in ("tz", "tn"):
            cnd = kept
        elif rm == "tp":
            cnd = kept + 1
        elif g == 0:
            cnd = kept
        elif r or st:
            cnd = kept + 1
        else:
            # Exact midpoint: ties-to-even stays, ties-to-away
            # (positive result) goes up. Counted, not assumed.
            TIES_SEEN.append((fmt, x, rm))
            if rm == "ta":
                cnd = kept + 1
            else:
                cnd = kept if kept % 2 == 0 else kept + 1
        ee = e2
        if cnd == (1 << p):
            cnd, ee = 1 << (p - 1), ee + 1
        assert q["emin"] <= ee <= q["emax"], (fmt, hex(x), rm, ee)
        bits = ((ee + bias) << t) | (cnd - (1 << t))
        out.append((bits, 0 if exact else INEXACT))
    return out


def decide(fmt, x):
    sp = decide_special(fmt, x)
    if sp is not None:
        return sp
    return decide_finite(fmt, x)


def main():
    # stdin lines: "FMT HEX" -> stdout "FMT HEX m0b m0f ... m4b m4f"
    for line in sys.stdin:
        tk = line.split()
        if not tk:
            continue
        fmt, x = tk[0], int(tk[1], 16)
        res = decide(fmt, x)
        print("D", fmt, "%x" % x,
              " ".join("%x %02x" % (b, f) for b, f in res))


if __name__ == "__main__":
    main()

