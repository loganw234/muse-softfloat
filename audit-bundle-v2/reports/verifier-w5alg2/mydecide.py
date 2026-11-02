#!/usr/bin/env python3
"""Verifier-w5alg2 OWN exact hypot decider (mydecide.py).

Independent integer/Fraction arithmetic written by the verifier from
the study design (scratch/sf2-algebraic/report.md Secs. 3.2/5.2):
evaluation-order specials, exact sum of squares S as a Fraction,
exact floor-root + midpoint compare at the delivered granularity,
Clause-7 flags derived from first principles (tininess after
rounding, overflow through the unbounded value). No MPFR, no copy
of the parcel generator, no kernel code is reused here.

Second half: a bit-accurate u128 window simulation (Python ints
masked to 128 bits) of three alignment forms --
  floor-full  : truncation + tail sticky, parity drop kept as sticky
                (the mandated floor-sum form of study Sec. 3.2);
  jam         : MSF_ALG_TEST_JAM form (shr_jam alignment + jammed
                parity bit, remainder-only sticky);
  dropped     : what the copy's C code actually feeds the pack
                (remainder-only sticky, tail/parity computed but
                never ORed in) --
each packed through an exact pack emulator that breaks ties from
the exact S. Adjudication inputs for the jam question.

Usage:
  mydecide.py decide   < lines "fi a b" (fi 0/1/2, hex pair, same-format)
                       -> per line 5x "bits flags" for te tz tp tn ta
  mydecide.py sim      < lines "fi a b"
                       -> per line: exact bits/flags x5 (main decider),
                          then floor-full / jam / dropped packed x5.
"""
import sys
from fractions import Fraction
from math import isqrt

MASK128 = (1 << 128) - 1

FMTS = {
    0: dict(name="f16", w=16, t=10, bias=15, emin=-14, emax=15),
    1: dict(name="f32", w=32, t=23, bias=127, emin=-126, emax=127),
    2: dict(name="f64", w=64, t=52, bias=1023, emin=-1022, emax=1023),
}
for _f in FMTS.values():
    _f["p"] = _f["t"] + 1
    _f["emaxf"] = (1 << (_f["w"] - 1 - _f["t"])) - 1
    _f["sign"] = 1 << (_f["w"] - 1)
    _f["qbit"] = 1 << (_f["t"] - 1)
    _f["inf"] = ((1 << (_f["w"] - 1 - _f["t"])) - 1) << _f["t"]
    _f["maxfin"] = ((((1 << (_f["w"] - 1 - _f["t"])) - 2) << _f["t"])
                    | ((1 << _f["t"]) - 1))
    _f["mask"] = (1 << _f["w"]) - 1

INVALID, DIVZERO, OVERFLOW, UNDERFLOW, INEXACT = 0x01, 0x02, 0x04, 0x08, 0x10
RMS = ("te", "tz", "tp", "tn", "ta")


def decode(fi, x):
    f = FMTS[fi]
    t = f["t"]
    ew = f["w"] - 1 - t
    emaxf = (1 << ew) - 1
    sign = (x >> (f["w"] - 1)) & 1
    ef = (x >> t) & emaxf
    frac = x & ((1 << t) - 1)
    if ef == emaxf:
        if frac == 0:
            return ("inf", sign, 0, 0)
        return ("qnan" if (frac >> (t - 1)) & 1 else "snan", sign, 0, frac)
    if ef == 0:
        if frac == 0:
            return ("zero", sign, 0, 0)
        return ("sub", sign, frac, f["emin"] - t)
    return ("norm", sign, frac | (1 << t), ef - f["bias"] - t)


def specials(fi, a, b):
    """9.2.1 evaluation order. Returns [(bits,flags)]x5 or None."""
    f = FMTS[fi]
    ca, sa, _, fa = decode(fi, a)
    cb, sb, _, fb = decode(fi, b)
    if ca == "snan" or cb == "snan":
        first = a if ca == "snan" else b
        return [((first | f["qbit"]) & f["mask"], INVALID)] * 5
    if ca == "inf" or cb == "inf":
        return [(f["inf"], 0)] * 5
    if ca == "qnan" or cb == "qnan":
        first = a if ca == "qnan" else b
        return [(first & f["mask"], 0)] * 5
    if ca == "zero" and cb == "zero":
        return [(0, 0)] * 5
    return None


def _choose(rm, n, exact, above_mid, on_mid):
    """Delivered significand multiple index at the working granularity.
    above_mid: True iff true value is strictly above the midpoint
    (n+1/2); on_mid: exactly on it. Caller guarantees not exact."""
    if rm in ("tz", "tn"):
        return n
    if rm == "tp":
        return n + 1
    if on_mid:
        if rm == "ta":
            return n + 1
        return n if n % 2 == 0 else n + 1
    return n + 1 if above_mid else n


def _floor_log2_sqrt(S):
    """e with 2^(2e) <= S < 2^(2e+2), S a positive Fraction."""
    e = (S.numerator.bit_length() - S.denominator.bit_length()) // 2
    while Fraction(2) ** (2 * (e + 1)) <= S:
        e += 1
    while Fraction(2) ** (2 * e) > S:
        e -= 1
    return e


def round_sqrt_exact(fi, S):
    """Correctly round sqrt(S), S a positive Fraction. [(bits,flags)]x5."""
    f = FMTS[fi]
    p = f["p"]
    e = _floor_log2_sqrt(S)
    out = []
    for rm in RMS:
        # Unbounded precision-p rounding w (the overflow judge).
        ulp_u = Fraction(2) ** (e - (p - 1))
        Ru = S / ulp_u**2
        n_u = isqrt(Ru.numerator // Ru.denominator)
        exact_u = Fraction(n_u * n_u) == Ru
        d4 = 4 * Ru - Fraction((2 * n_u + 1) ** 2)
        above_u, on_u = d4 > 0, d4 == 0
        w = Fraction(n_u if exact_u else _choose(rm, n_u, False,
                                                above_u, on_u)) * ulp_u
        if w >= Fraction(2) ** (f["emax"] + 1):
            bits = f["inf"] if rm in ("te", "ta", "tp") else f["maxfin"]
            out.append((bits, OVERFLOW | INEXACT))
            continue
        tiny = w < Fraction(2) ** f["emin"]
        ulp_d = ulp_u if e >= f["emin"] else Fraction(2) ** (f["emin"] - (p - 1))
        Rd = S / ulp_d**2
        n_d = isqrt(Rd.numerator // Rd.denominator)
        exact_d = Fraction(n_d * n_d) == Rd
        d4d = 4 * Rd - Fraction((2 * n_d + 1) ** 2)
        c = n_d if exact_d else _choose(rm, n_d, False, d4d > 0, d4d == 0)
        val = Fraction(c) * ulp_d
        bits = encode_value(fi, val)
        inexact = (val * val != S)
        flags = 0
        if inexact:
            flags |= INEXACT
            if tiny:
                flags |= UNDERFLOW
        out.append((bits, flags))
    return out


def encode_value(fi, v):
    """Bits of a nonnegative exactly-representable value."""
    f = FMTS[fi]
    t = f["t"]
    assert v >= 0
    if v == 0:
        return 0
    if v >= Fraction(2) ** f["emin"]:
        e = v.numerator.bit_length() - v.denominator.bit_length()
        while Fraction(2) ** (e + 1) <= v:
            e += 1
        while Fraction(2) ** e > v:
            e -= 1
        scaled = v / Fraction(2) ** (e - t)
        assert scaled.denominator == 1, (fi, v)
        return ((e + f["bias"]) << t) | (int(scaled) - (1 << t))
    scaled = v / Fraction(2) ** (f["emin"] - t)
    assert scaled.denominator == 1 and 0 < scaled < (1 << t), (fi, v)
    return int(scaled)


def decide(fi, a, b):
    sp = specials(fi, a, b)
    if sp is not None:
        return sp
    _, _, sa, ea = decode(fi, a)
    _, _, sb, eb = decode(fi, b)
    S = (Fraction(sa * sa) * Fraction(2) ** (2 * ea)
         + Fraction(sb * sb) * Fraction(2) ** (2 * eb))
    assert S > 0
    return round_sqrt_exact(fi, S)


# ---- bit-accurate u128 window simulation (jam adjudication) ----

def _order(fi, a, b):
    """Return (A,B) magnitudes ordered |A|>=|B| as (sig,exp) pairs."""
    _, _, sa, ea = decode(fi, a)
    _, _, sb, eb = decode(fi, b)
    va = Fraction(sa) * Fraction(2) ** ea
    vb = Fraction(sb) * Fraction(2) ** eb
    if va < vb:
        return (sb, eb), (sa, ea)
    return (sa, ea), (sb, eb)


def window_sim(fi, a, b, form):
    """Simulate one alignment form. form in floor-full/jam/dropped.
    Returns (Q, sticky_for_pack, rad, Ew) with Q the integer root,
    Ew the (even) radicand scale exponent, sticky_for_pack the bit
    the pack would receive under that form's sticky rule."""
    assert specials(fi, a, b) is None
    (sa, ea), (sb, eb) = _order(fi, a, b)
    SA, SB = sa * sa, sb * sb
    la2 = SA.bit_length()
    lsh = 121 - la2
    a_win = (SA << lsh) & MASK128
    net = lsh - 2 * (ea - eb)
    if net >= 0:
        b_win, tail = (SB << net) & MASK128, 0
    elif form == "jam":
        k = -net
        dropped = SB & ((1 << k) - 1) if k < 1000 else (SB != 0)
        b_win = ((SB >> k) | (1 if dropped else 0)) & MASK128
        tail = 0  # jammed into the window, not kept aside
    else:
        k = -net
        tail = 1 if (SB & ((1 << k) - 1)) != 0 else 0
        b_win = (SB >> k) & MASK128
    tot = (a_win + b_win) & MASK128
    assert tot < (1 << 122), (fi, hex(a), hex(b))
    ew = 2 * ea - lsh
    if ew % 2 != 0:
        if form == "jam":
            rad = ((tot >> 1) | (tot & 1)) & MASK128
            pdrop = 0
        else:
            pdrop = tot & 1
            rad = (tot >> 1) & MASK128
        ew += 1
    else:
        rad, pdrop = tot, 0
    Q = isqrt(rad)
    rem = rad - Q * Q
    if form == "floor-full":
        sticky = 1 if (tail or pdrop or rem != 0) else 0
    else:
        # jam shares remainder-only sticky by construction; dropped
        # is the copy's actual code (tail/parity never ORed in).
        sticky = 1 if rem != 0 else 0
    return Q, sticky, rad, ew, tail, pdrop, rem != 0


def pack_pure(fi, E, Q, sticky):
    """The pack as a pure function of its fed (Q, sticky) at scale E:
    value (Q+f)*2^E with f=0 iff sticky==0 else 0<f<1. Guard/round/
    sticky come from Q's bits below the destination ulp; the unknown
    f can only hide strictly inside one Q-ulp. Returns [(bits,flags)]
    x5 for te tz tp tn ta. No truth oracle is consulted."""
    f = FMTS[fi]
    p = f["p"]
    # fed binade from the fed floor (a power of two cannot hide
    # strictly inside the fed sliver: both ends are multiples of
    # 2^E, so e computed here equals the truth's binade).
    e = (Q * Q).bit_length() // 2 + E
    while Fraction(2) ** (2 * (e + 1)) <= Fraction(Q * Q) * Fraction(2) ** (2 * E):
        e += 1
    while Fraction(2) ** (2 * e) > Fraction(Q * Q) * Fraction(2) ** (2 * E):
        e -= 1
    out = []
    for rm in RMS:
        ulp_u = Fraction(2) ** (e - (p - 1))
        shift = E - (e - (p - 1))  # Q-ulp in units of ulp_u: 2^shift
        if shift >= 0:
            n_u, g, r, s_rest = Q << shift, 0, 0, 0
        else:
            n_u = Q >> (-shift)
            low = Q & ((1 << (-shift)) - 1)
            g = (low >> (-shift - 1)) & 1 if -shift >= 1 else 0
            r = (low >> (-shift - 2)) & 1 if -shift >= 2 else 0
            s_rest = 1 if (-shift >= 3 and (low & ((1 << (-shift - 2)) - 1))) else 0
        s = s_rest or sticky
        fracbits = 0 if shift >= 0 else low
        exact = (sticky == 0 and fracbits == 0 and shift <= 0) or \
                (sticky == 0 and shift >= 0)
        on_mid = bool(g and not r and not s)
        above_mid = bool(g and (r or s))
        if exact:
            c = n_u
        elif rm in ("tz", "tn"):
            c = n_u
        elif rm == "tp":
            c = n_u + 1
        elif on_mid:
            c = n_u + 1 if rm == "ta" else (n_u if n_u % 2 == 0 else n_u + 1)
        else:
            c = n_u + 1 if above_mid else n_u
        w = Fraction(c) * ulp_u
        if w >= Fraction(2) ** (f["emax"] + 1):
            bits = f["inf"] if rm in ("te", "ta", "tp") else f["maxfin"]
            out.append((bits, OVERFLOW | INEXACT))
            continue
        tiny = w < Fraction(2) ** f["emin"]
        if e >= f["emin"]:
            # inexact ⟺ the fed value is not exactly the delivered
            # multiple (fed exact and c == fed floor multiple).
            inexact = not (exact and c == n_u)
            flags = 0
            if inexact:
                flags |= INEXACT
                if tiny:
                    flags |= UNDERFLOW
            out.append((encode_value(fi, w), flags))
            continue
        # subnormal clamp: re-decide at the subnormal granularity.
        ulp_d = Fraction(2) ** (f["emin"] - (p - 1))
        shift_d = E - (f["emin"] - (p - 1))
        if shift_d >= 0:
            n_d, gd, rd, sd_rest = Q << shift_d, 0, 0, 0
            lowd = 0
        else:
            n_d = Q >> (-shift_d)
            lowd = Q & ((1 << (-shift_d)) - 1)
            gd = (lowd >> (-shift_d - 1)) & 1 if -shift_d >= 1 else 0
            rd = (lowd >> (-shift_d - 2)) & 1 if -shift_d >= 2 else 0
            sd_rest = 1 if (-shift_d >= 3 and (lowd & ((1 << (-shift_d - 2)) - 1))) else 0
        sd = sd_rest or sticky
        exactd = (sticky == 0 and lowd == 0)
        on_midd = bool(gd and not rd and not sd)
        above_midd = bool(gd and (rd or sd))
        if exactd:
            cd = n_d
        elif rm in ("tz", "tn"):
            cd = n_d
        elif rm == "tp":
            cd = n_d + 1
        elif on_midd:
            cd = n_d + 1 if rm == "ta" else (n_d if n_d % 2 == 0 else n_d + 1)
        else:
            cd = n_d + 1 if above_midd else n_d
        val = Fraction(cd) * ulp_d
        fed_is_mult_d = (lowd == 0)
        inexact = not (exactd and cd == n_d and fed_is_mult_d)
        flags = 0
        if inexact:
            flags |= INEXACT
            if tiny:
                flags |= UNDERFLOW
        out.append((encode_value(fi, val), flags))
    return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "decide"
    for line in sys.stdin:
        tk = line.split()
        if len(tk) != 3:
            continue
        fi, a, b = int(tk[0]), int(tk[1], 16), int(tk[2], 16)
        exp = decide(fi, a, b)
        print(" ".join(f"{rb:x} {rf:02x}" for rb, rf in exp))
        if mode == "sim":
            if specials(fi, a, b) is not None:
                print("special")
                continue
            _, _, sa, ea = decode(fi, a)
            _, _, sb, eb = decode(fi, b)
            S = (Fraction(sa * sa) * Fraction(2) ** (2 * ea)
                 + Fraction(sb * sb) * Fraction(2) ** (2 * eb))
            # consistency: fed slivers must bracket the truth, and a
            # power of two cannot hide strictly inside any sliver.
            row = []
            for form in ("floor-full", "jam", "dropped"):
                Q, st, _, ew, _, _, _ = window_sim(fi, a, b, form)
                E = ew // 2
                if form != "jam":
                    # floor forms share Q: bracket must hold, with
                    # equality iff the form's own sticky is zero.
                    flo = Fraction(Q * Q) * Fraction(2) ** (2 * E)
                    hi = Fraction((Q + 1) * (Q + 1)) * Fraction(2) ** (2 * E)
                    if st == 0:
                        assert S == flo, (form, fi, hex(a), hex(b))
                    else:
                        assert flo < S < hi, (form, fi, hex(a), hex(b))
                row.append(pack_pure(fi, E, Q, st))
            print("sim " + " | ".join(
                " ".join(f"{rb:x} {rf:02x}" for rb, rf in r) for r in row))


if __name__ == "__main__":
    sys.exit(main())
