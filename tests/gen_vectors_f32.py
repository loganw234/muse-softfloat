#!/usr/bin/env python3
"""Project-exact references for the binary32 wave-1 instantiations.

Test code only (SF-0 4.3). Expected values are computed from the
decoded integers with exact rational arithmetic (Fraction), never
by calling the implementation and never through hardware types.
Special-value rules follow IEEE 754-2019 Clauses 6 and 7 with the
SF-0 2.5 NaN matrix and the project rulings recorded in the
parcel-f32 ledger design entry:

- scaleB non-integral N truncates toward zero; infinite N acts as
  a saturating exponent of its sign.
- convertToIntegerExact* signals inexact only when the rounded
  integer is in range; out-of-range and non-finite signal invalid
  only, delivering the header saturation rule.

Usage:
  gen_vectors_f32.py directed OUTDIR     committed directed sets
  gen_vectors_f32.py sweep OUTFILE N SEED  seeded cross-format sweep
"""
import random
import sys
from fractions import Fraction
from pathlib import Path

FLAG_INV, FLAG_DIV0, FLAG_OVF, FLAG_UNF, FLAG_INX = 0x01, 0x02, 0x04, 0x08, 0x10
RMS4 = ["te", "tz", "tp", "tn"]

FMT = {  # name: (bits, precision, exp bits)
    "f32": (32, 24, 8),
    "f64": (64, 53, 11),
}


def fmt_consts(fmt):
    bits, p, w = FMT[fmt]
    t = bits - 1 - w
    emax = (1 << (w - 1)) - 1
    return {
        "bits": bits, "p": p, "w": w, "t": t, "emax": emax,
        "emin": 1 - emax, "bias": emax,
        "signbit": 1 << (bits - 1),
        "expmax": (1 << w) - 1,
        "fracmask": (1 << t) - 1,
        "quiet": 1 << (t - 1),
        "inf": ((1 << w) - 1) << t,
    }


class Dec:
    __slots__ = ("fmt", "bits", "sign", "cls", "sig", "exp", "frac")

    def __init__(self, fmt, bits):
        c = fmt_consts(fmt)
        self.fmt = fmt
        self.bits = bits
        self.sign = 1 if bits & c["signbit"] else 0
        e = (bits >> c["t"]) & c["expmax"]
        self.frac = bits & c["fracmask"]
        if e == c["expmax"]:
            self.sig = self.frac
            self.exp = 0
            self.cls = ("inf" if self.frac == 0 else
                        ("qnan" if self.frac & c["quiet"] else "snan"))
        elif e == 0:
            self.sig = self.frac
            self.exp = c["emin"] - c["t"]
            self.cls = "zero" if self.frac == 0 else "finite"
        else:
            self.sig = self.frac | (1 << c["t"])
            self.exp = e - c["bias"] - c["t"]
            self.cls = "finite"

    def value(self):
        """Exact signed value for finite/zero classes."""
        if self.exp >= 0:
            v = Fraction(self.sig << self.exp)
        else:
            v = Fraction(self.sig, 1 << (-self.exp))
        return -v if self.sign else v


def isnan(d):
    return d.cls in ("qnan", "snan")


def default_qnan(fmt):
    c = fmt_consts(fmt)
    return c["inf"] | c["quiet"]


def nan_to_dest(dfmt, src):
    dc, sc = fmt_consts(dfmt), fmt_consts(src.fmt)
    if dc["t"] >= sc["t"]:
        payload = src.frac << (dc["t"] - sc["t"])
    else:
        payload = src.frac >> (sc["t"] - dc["t"])
    if payload == 0:
        return default_qnan(dfmt)
    return (dc["signbit"] if src.sign else 0) | dc["inf"] | payload | dc["quiet"]


def nan_delivery(dfmt, ops, invalid_without_nan):
    """SF-0 2.5 chain. Return (bits, invalid_flag) or (None, False)."""
    for d in ops:
        if d.cls == "snan":
            return nan_to_dest(dfmt, d), True
    for d in ops:
        if d.cls == "qnan":
            return nan_to_dest(dfmt, d), False
    if invalid_without_nan:
        return default_qnan(dfmt), True
    return None, False


def floor_log2_frac(fr):
    e = fr.numerator.bit_length() - fr.denominator.bit_length()
    if e >= 0:
        if fr.numerator < (fr.denominator << e):
            e -= 1
    else:
        if (fr.numerator << (-e)) < fr.denominator:
            e -= 1
    return e


def pack_mag(sign, mag, rm, fmt):
    """Round exact magnitude Fraction mag once into fmt (Clause 7,
    tininess after rounding). Return (bits, flags)."""
    c = fmt_consts(fmt)
    p, t, emax, emin = c["p"], c["t"], c["emax"], c["emin"]
    if mag == 0:
        return (c["signbit"] if sign else 0), 0
    e = floor_log2_frac(mag)
    scale = max(e, emin) - (p - 1)
    num, den = mag.numerator, mag.denominator
    if scale >= 0:
        den <<= scale
    else:
        num <<= -scale
    q, r = divmod(num, den)
    inexact = r != 0
    inc = False
    if inexact:
        twice = 2 * r
        if rm == "te":
            inc = twice > den or (twice == den and q % 2 == 1)
        elif rm == "ta":
            inc = twice >= den
        elif rm == "tp":
            inc = not sign
        elif rm == "tn":
            inc = bool(sign)
    if inc:
        q += 1
    if q == (1 << p):
        q >>= 1
        scale += 1
    # Tininess after rounding (Clause 7.5, lead ruling 2026-10-26):
    # judge the p-bit rounding at the value's own binade scale (as
    # though the exponent range were unbounded) against 2^emin.
    tiny_u = False
    if e < emin:
        scale_u = e - (p - 1)
        numu, denu = mag.numerator, mag.denominator
        if scale_u >= 0:
            denu <<= scale_u
        else:
            numu <<= -scale_u
        q_u, r_u = divmod(numu, denu)
        if r_u:
            twice_u = 2 * r_u
            if rm == "te":
                q_u += 1 if (twice_u > denu or (twice_u == denu and q_u % 2 == 1)) else 0
            elif rm == "ta":
                q_u += 1 if twice_u >= denu else 0
            elif rm == "tp":
                q_u += 0 if sign else 1
            elif rm == "tn":
                q_u += 1 if sign else 0
        tiny_u = (e + 1 if q_u == (1 << p) else e) < emin
    signbit = c["signbit"] if sign else 0
    if q >= (1 << (p - 1)):
        big_e = scale + (p - 1)
        if big_e > emax:
            to_inf = rm in ("te", "ta") or (rm == "tp" and not sign) \
                or (rm == "tn" and sign)
            enc = c["inf"] if to_inf else ((c["expmax"] - 1) << t) | c["fracmask"]
            return signbit | enc, FLAG_OVF | FLAG_INX
        flags = 0
        if inexact:
            flags = FLAG_INX | (FLAG_UNF if tiny_u else 0)
        return (signbit | ((big_e + c["bias"]) << t) | (q - (1 << (p - 1))),
                flags)
    flags = 0
    if inexact:
        flags = FLAG_INX | (FLAG_UNF if tiny_u else 0)
    return signbit | q, flags


def pack_signed(value, rm, fmt):
    return pack_mag(1 if value < 0 else 0, abs(value), rm, fmt)


def pack_sticky_mag(sign, q, exp, sticky, rm, fmt):
    """Pack a value in [q, q+1) * 2^exp, equal to q*2^exp iff not
    sticky, with q carrying far more than p bits. Substituting the
    midpoint (2q+1)/2 cannot cross a rounding boundary: boundary
    positions are multiples of a whole number of q units."""
    mag = Fraction(2 * q + (1 if sticky else 0), 2)
    if exp >= 0:
        mag *= 1 << exp
    else:
        mag /= 1 << (-exp)
    return pack_mag(sign, mag, rm, fmt)


def round_signed_frac(fr, mode):
    """Round a signed Fraction to a signed integer per mode."""
    sign = fr < 0
    mag = -fr if sign else fr
    q = mag.numerator // mag.denominator
    r = mag - q
    inc = False
    if r:
        if mode == "te":
            inc = r > Fraction(1, 2) or (r == Fraction(1, 2) and q % 2 == 1)
        elif mode == "ta":
            inc = r >= Fraction(1, 2)
        elif mode == "tp":
            inc = not sign
        elif mode == "tn":
            inc = sign
    q += 1 if inc else 0
    return -q if sign else q


def zero_bits(fmt, sign):
    return fmt_consts(fmt)["signbit"] if sign else 0


def inf_bits(fmt, sign):
    c = fmt_consts(fmt)
    return (c["signbit"] if sign else 0) | c["inf"]


# ---------------- operation references (destination binary32
# except log_b, whose destination is binary64) ----------------

def ref_addsub(afmt, a, bfmt, b, issub, rm):
    da, db = Dec(afmt, a), Dec(bfmt, b)
    effb = db.sign ^ (1 if issub else 0)
    inv = da.cls == "inf" and db.cls == "inf" and da.sign != effb
    bits, bad = nan_delivery("f32", [da, db], inv)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    if da.cls == "inf":
        return inf_bits("f32", da.sign), 0
    if db.cls == "inf":
        return inf_bits("f32", effb), 0
    va, vb = da.value(), db.value()
    exact = va - vb if issub else va + vb
    if exact == 0:
        if va == 0 and vb == 0 and da.sign == effb:
            return zero_bits("f32", da.sign), 0
        return zero_bits("f32", 1 if rm == "tn" else 0), 0
    return pack_signed(exact, rm, "f32")


def ref_mul(afmt, a, bfmt, b, rm):
    da, db = Dec(afmt, a), Dec(bfmt, b)
    sign = da.sign ^ db.sign
    inv = (da.cls == "zero" and db.cls == "inf") or \
          (da.cls == "inf" and db.cls == "zero")
    bits, bad = nan_delivery("f32", [da, db], inv)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    if da.cls == "inf" or db.cls == "inf":
        return inf_bits("f32", sign), 0
    if da.cls == "zero" or db.cls == "zero":
        return zero_bits("f32", sign), 0
    return pack_signed(da.value() * db.value(), rm, "f32")


def ref_div(afmt, a, bfmt, b, rm):
    da, db = Dec(afmt, a), Dec(bfmt, b)
    sign = da.sign ^ db.sign
    inv = (da.cls == "zero" and db.cls == "zero") or \
          (da.cls == "inf" and db.cls == "inf")
    bits, bad = nan_delivery("f32", [da, db], inv)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    if da.cls == "inf":
        return inf_bits("f32", sign), 0
    if db.cls == "inf":
        return zero_bits("f32", sign), 0
    if db.cls == "zero":
        return inf_bits("f32", sign), FLAG_DIV0
    if da.cls == "zero":
        return zero_bits("f32", sign), 0
    return pack_signed(da.value() / db.value(), rm, "f32")


def ref_sqrt(afmt, a, rm):
    import math
    da = Dec(afmt, a)
    inv = bool(da.sign) and da.cls in ("inf", "finite")
    bits, bad = nan_delivery("f32", [da], inv)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    if da.cls == "inf":
        return inf_bits("f32", 0), 0
    if da.cls == "zero":
        return zero_bits("f32", da.sign), 0
    sig, exp = da.sig, da.exp
    if exp % 2:
        sig <<= 1
        exp -= 1
    shift = 160
    scaled = sig << shift
    q = math.isqrt(scaled)
    return pack_sticky_mag(0, q, exp // 2 - shift // 2,
                           scaled != q * q, rm, "f32")


def ref_fma(afmt, a, bfmt, b, cfmt, c, rm):
    da, db, dc = Dec(afmt, a), Dec(bfmt, b), Dec(cfmt, c)
    psign = da.sign ^ db.sign
    prod_zero_inf = (da.cls == "zero" and db.cls == "inf") or \
                    (da.cls == "inf" and db.cls == "zero")
    prod_inf = (da.cls == "inf" and not isnan(db) and db.cls != "zero") or \
               (db.cls == "inf" and not isnan(da) and da.cls != "zero")
    inv = prod_zero_inf or (prod_inf and dc.cls == "inf" and psign != dc.sign)
    extra = FLAG_INV if (prod_zero_inf and dc.cls == "qnan") else 0
    bits, bad = nan_delivery("f32", [da, db, dc], inv)
    if bits is not None:
        return bits, extra | (FLAG_INV if bad else 0)
    if prod_inf:
        return inf_bits("f32", psign), 0
    if dc.cls == "inf":
        return inf_bits("f32", dc.sign), 0
    prod = da.value() * db.value()
    exact = prod + dc.value()
    if exact == 0:
        if prod == 0 and dc.value() == 0 and psign == dc.sign:
            return zero_bits("f32", psign), 0
        return zero_bits("f32", 1 if rm == "tn" else 0), 0
    return pack_signed(exact, rm, "f32")


def ref_remainder(a, b):
    da, db = Dec("f32", a), Dec("f32", b)
    inv = da.cls == "inf" or db.cls == "zero"
    bits, bad = nan_delivery("f32", [da, db], inv)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    if db.cls == "inf" or da.cls == "zero":
        return a, 0
    va, vb = da.value(), db.value()
    n = round_signed_frac(va / vb, "te")
    r = va - n * vb
    if r == 0:
        return zero_bits("f32", da.sign), 0
    bits, flags = pack_signed(r, "te", "f32")
    assert Dec("f32", bits).value() == r and flags == 0, (a, b, bits, flags)
    return bits, flags


def ref_rint(a, mode, exact_form, rm_attr):
    da = Dec("f32", a)
    bits, bad = nan_delivery("f32", [da], False)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    if da.cls in ("inf", "zero"):
        return a, 0
    v = da.value()
    k = round_signed_frac(v, rm_attr if exact_form else mode)
    flags = FLAG_INX if (exact_form and Fraction(k) != v) else 0
    if k == 0:
        return zero_bits("f32", da.sign), flags
    bits, pflags = pack_signed(Fraction(k), "te", "f32")
    assert pflags == 0 and Dec("f32", bits).value() == k
    return bits, flags


def ref_next(a, up):
    da = Dec("f32", a)
    bits, bad = nan_delivery("f32", [da], False)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    c = fmt_consts("f32")
    maxfinite = ((c["expmax"] - 1) << c["t"]) | c["fracmask"]
    if da.cls == "inf":
        if up:
            return (c["signbit"] | maxfinite, 0) if da.sign else (a, 0)
        return (a, 0) if da.sign else (maxfinite, 0)
    if da.cls == "zero":
        return (1, 0) if up else (c["signbit"] | 1, 0)
    if up:
        return (a - 1 if da.sign else a + 1), 0
    return (a + 1 if da.sign else a - 1), 0


def ref_scaleb(a, nbits, rm):
    dx, dn = Dec("f32", a), Dec("f64", nbits)
    bits, bad = nan_delivery("f32", [dx, dn], False)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    if dx.cls in ("inf", "zero"):
        return a, 0
    if dn.cls == "zero":
        return a, 0
    if dn.cls == "inf":
        n = -3000 if dn.sign else 3000
    else:
        n = int(dn.value())
        n = max(-3000, min(3000, n))
    if n == 0:
        return a, 0
    exact = dx.value() * (Fraction(2) ** n)
    return pack_signed(exact, rm, "f32")


def ref_logb(a):
    da = Dec("f32", a)
    bits, bad = nan_delivery("f64", [da], False)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    if da.cls == "zero":
        return inf_bits("f64", 1), FLAG_DIV0
    if da.cls == "inf":
        return inf_bits("f64", 0), 0
    e = floor_log2_frac(abs(da.value()))
    if e == 0:
        return 0, 0
    bits, flags = pack_mag(1 if e < 0 else 0, Fraction(abs(e)), "te", "f64")
    assert flags == 0
    return bits, flags


def ref_conv(sfmt, a, rm):
    da = Dec(sfmt, a)
    bits, bad = nan_delivery("f32", [da], False)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    if da.cls == "inf":
        return inf_bits("f32", da.sign), 0
    if da.cls == "zero":
        return zero_bits("f32", da.sign), 0
    return pack_signed(da.value(), rm, "f32")


def ref_from_int(ival, rm):
    return pack_signed(Fraction(ival), rm, "f32")


INT_KINDS = {  # token: (signed, width)
    "i8": (1, 8), "u8": (0, 8), "i16": (1, 16), "u16": (0, 16),
    "i32": (1, 32), "u32": (0, 32), "i64": (1, 64), "u64": (0, 64),
}
INT_MODES = [
    ("ties_to_even", "te", 0), ("ties_to_away", "ta", 0),
    ("toward_zero", "tz", 0), ("toward_positive", "tp", 0),
    ("toward_negative", "tn", 0),
    ("exact_ties_to_even", "te", 1), ("exact_ties_to_away", "ta", 1),
    ("exact_toward_zero", "tz", 1), ("exact_toward_positive", "tp", 1),
    ("exact_toward_negative", "tn", 1),
]


def ref_to_int(a, tok, mode, exact_form):
    da = Dec("f32", a)
    is_signed, width = INT_KINDS[tok]
    lo = -(1 << (width - 1)) if is_signed else 0
    hi = (1 << (width - 1)) - 1 if is_signed else (1 << width) - 1
    mask = (1 << width) - 1
    if isnan(da):
        return 0, FLAG_INV
    if da.cls == "inf":
        return (lo if da.sign else hi) & mask, FLAG_INV
    v = da.value()
    k = round_signed_frac(v, mode)
    if k < lo or k > hi:
        return (lo if k < lo else hi) & mask, FLAG_INV
    flags = FLAG_INX if (exact_form and Fraction(k) != v) else 0
    return k & mask, flags


REL = {"lt": 1, "eq": 2, "gt": 4, "un": 8}
CMP_PREDS = [  # (name suffix, relation set, signaling family)
    ("quiet_equal", "eq", 0), ("quiet_not_equal", "lt,gt,un", 0),
    ("signaling_equal", "eq", 1), ("signaling_not_equal", "lt,gt,un", 1),
    ("quiet_greater", "gt", 0), ("quiet_greater_equal", "gt,eq", 0),
    ("quiet_less", "lt", 0), ("quiet_less_equal", "lt,eq", 0),
    ("quiet_not_greater", "lt,eq,un", 0), ("quiet_not_less", "gt,eq,un", 0),
    ("quiet_less_unordered", "lt,un", 0),
    ("quiet_greater_unordered", "gt,un", 0),
    ("quiet_unordered", "un", 0), ("quiet_ordered", "lt,eq,gt", 0),
    ("signaling_greater", "gt", 1), ("signaling_greater_equal", "gt,eq", 1),
    ("signaling_less", "lt", 1), ("signaling_less_equal", "lt,eq", 1),
    ("signaling_not_greater", "lt,eq,un", 1),
    ("signaling_not_less", "gt,eq,un", 1),
    ("signaling_less_unordered", "lt,un", 1),
    ("signaling_greater_unordered", "gt,un", 1),
]


def ref_compare(afmt, a, bfmt, b, relset, signaling):
    da, db = Dec(afmt, a), Dec(bfmt, b)
    flags = 0
    if isnan(da) or isnan(db):
        rel = "un"
        if da.cls == "snan" or db.cls == "snan" or signaling:
            flags = FLAG_INV
    else:
        def rank(d):
            if d.cls == "inf":
                return -(Fraction(10) ** 400) if d.sign else Fraction(10) ** 400
            return d.value()
        ra, rb = rank(da), rank(db)
        rel = "lt" if ra < rb else ("gt" if ra > rb else "eq")
    return (1 if rel in relset.split(",") else 0), flags


def total_rank(bits):
    d = Dec("f32", bits)
    if d.cls == "qnan" and d.sign:
        return (0, -d.frac)
    if d.cls == "snan" and d.sign:
        return (1, -d.frac)
    if d.cls == "inf" and d.sign:
        return (2, 0)
    if d.sign and d.cls == "finite":
        return (3, d.value())
    if d.sign and d.cls == "zero":
        return (4, 0)
    if not d.sign and d.cls == "zero":
        return (5, 0)
    if not d.sign and d.cls == "finite":
        return (6, d.value())
    if d.cls == "inf":
        return (7, 0)
    if d.cls == "snan":
        return (8, d.frac)
    return (9, d.frac)


def ref_total_order(a, b, mag):
    if mag:
        s = fmt_consts("f32")["signbit"]
        a, b = a & ~s, b & ~s
    return (1 if total_rank(a) <= total_rank(b) else 0), None


# ---------------- operand pools ----------------

def enc_fields(fmt, sign, expfield, frac):
    c = fmt_consts(fmt)
    return (c["signbit"] if sign else 0) | (expfield << c["t"]) | frac


def enc_exact_frac(fmt, frac_value):
    """Encode a Fraction that must be exact in fmt."""
    bits, flags = pack_signed(frac_value, "te", fmt)
    assert flags == 0 and Dec(fmt, bits).value() == frac_value, (fmt, frac_value)
    return bits


def make_pool(fmt):
    """32 semantic operand positions, parallel across formats."""
    c = fmt_consts(fmt)
    bias, t, emax = c["bias"], c["t"], c["emax"]
    one = enc_fields(fmt, 0, bias, 0)
    maxfinite = ((c["expmax"] - 1) << t) | c["fracmask"]
    pool = [
        enc_fields(fmt, 0, 0, 0),                       # 0 +0
        enc_fields(fmt, 1, 0, 0),                       # 1 -0
        enc_fields(fmt, 0, 0, 1),                       # 2 +minsub
        enc_fields(fmt, 1, 0, 1),                       # 3 -minsub
        enc_fields(fmt, 0, 0, c["fracmask"]),           # 4 +maxsub
        enc_fields(fmt, 0, 1, 0),                       # 5 +minnorm
        enc_fields(fmt, 1, 1, 0),                       # 6 -minnorm
        one,                                            # 7 +1
        enc_fields(fmt, 1, bias, 0),                    # 8 -1
        one + 1,                                        # 9 1+ulp
        one - 1,                                        # 10 1-ulp
        enc_exact_frac(fmt, Fraction(2)),               # 11
        enc_exact_frac(fmt, Fraction(1, 2)),            # 12
        enc_exact_frac(fmt, Fraction(3, 2)),            # 13
        enc_exact_frac(fmt, Fraction(-3, 2)),           # 14
        enc_exact_frac(fmt, Fraction(5, 2)),            # 15
        maxfinite,                                      # 16 maxfinite
        c["signbit"] | maxfinite,                       # 17 -maxfinite
        enc_exact_frac(fmt, Fraction(2) ** (emax - 1)),  # 18 large
        enc_exact_frac(fmt, Fraction(2) ** (c["emin"] + 1)),  # 19 tiny
        enc_exact_frac(fmt, Fraction(3)),               # 20
        enc_exact_frac(fmt, Fraction(-3)),              # 21
        c["inf"],                                       # 22 +inf
        c["signbit"] | c["inf"],                        # 23 -inf
        c["inf"] | c["quiet"],                          # 24 default qNaN
        c["signbit"] | c["inf"] | c["quiet"] | 0x12345 & c["fracmask"],  # 25
        c["inf"] | 1,                                   # 26 sNaN low payload
        c["signbit"] | c["inf"] | (c["quiet"] - 1),     # 27 -sNaN
        enc_exact_frac(fmt, Fraction(2) ** c["p"]),     # 28 2^p
        enc_exact_frac(fmt, Fraction(2) ** c["p"] - 1),  # 29 2^p-1
        pack_mag(0, Fraction(1, 10), "te", fmt)[0],     # 30 ~0.1
        pack_mag(1, Fraction(1, 10), "te", fmt)[0],     # 31 ~-0.1
    ]
    assert len(pool) == 32
    return pool


POOL32 = make_pool("f32")
POOL64 = make_pool("f64")
POOLS = {"f32": POOL32, "f64": POOL64}


def vline(op, rm, args, result, flags, prov):
    fl = "--" if flags is None else "%02x" % flags
    return "%s %s %s -> %x %s %s" % (
        op, rm, " ".join("%x" % a for a in args), result, fl, prov)


HDR = "# generated by tests/gen_vectors_f32.py - do not edit (regenerate)\n"


def write_file(path, lines):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    data = HDR + "\n".join(lines) + "\n"
    Path(path).write_bytes(data.encode("utf-8"))
    print("wrote %s (%d lines, %d bytes)" % (path, len(lines), len(data)))
    return len(data)


SPECIAL_IDX = [0, 1, 2, 3, 7, 8, 22, 23, 24, 26]
NUM_PAIRS = [(7, 8), (8, 7), (7, 7), (9, 10), (10, 9), (4, 2), (2, 4),
             (5, 4), (4, 5), (16, 16), (16, 18), (18, 18), (2, 2), (19, 2),
             (13, 14), (20, 21), (28, 7), (7, 28), (29, 7), (30, 30),
             (30, 31), (16, 7), (7, 16), (5, 5), (6, 5), (11, 12), (15, 13),
             (3, 3), (25, 7), (7, 27)]

BINOPS = [("add", lambda af, a, bf, b, rm: ref_addsub(af, a, bf, b, False, rm)),
          ("sub", lambda af, a, bf, b, rm: ref_addsub(af, a, bf, b, True, rm)),
          ("mul", ref_mul), ("div", ref_div)]


def opname_bin(op, afmt, bfmt):
    if afmt == bfmt == "f32":
        return "msf32_%s" % op
    return "msf32_%s_%s_%s" % (op, afmt, bfmt)


def gen_arith(prov):
    out = []
    for op, fn in BINOPS:
        for afmt in ("f32", "f64"):
            for bfmt in ("f32", "f64"):
                name = opname_bin(op, afmt, bfmt)
                pa, pb = POOLS[afmt], POOLS[bfmt]
                for i in SPECIAL_IDX:
                    for j in SPECIAL_IDX:
                        r, f = fn(afmt, pa[i], bfmt, pb[j], "te")
                        out.append(vline(name, "te", [pa[i], pb[j]], r, f, prov))
                for (i, j) in NUM_PAIRS:
                    for rm in RMS4:
                        r, f = fn(afmt, pa[i], bfmt, pb[j], rm)
                        out.append(vline(name, rm, [pa[i], pb[j]], r, f, prov))
    return out


FMA_TRIPLES = [
    (7, 7, 8), (7, 7, 7), (0, 22, 24), (22, 0, 24), (0, 22, 7), (22, 7, 23),
    (22, 7, 22), (7, 7, 22), (2, 2, 2), (16, 11, 0), (16, 7, 17), (13, 13, 14),
    (28, 7, 8), (9, 9, 10), (30, 30, 31), (5, 12, 2), (4, 11, 3), (24, 7, 7),
    (7, 26, 7), (7, 7, 27), (0, 7, 0), (1, 7, 0), (1, 8, 1), (20, 20, 21),
    (12, 12, 12), (18, 11, 17), (19, 12, 19), (29, 7, 29), (15, 11, 14),
    (6, 7, 5), (3, 11, 2), (10, 10, 8), (31, 31, 30), (25, 26, 24),
    (22, 22, 22), (0, 0, 23),
]


def gen_fma_sqrt(prov):
    out = []
    for afmt in ("f32", "f64"):
        for bfmt in ("f32", "f64"):
            for cfmt in ("f32", "f64"):
                if afmt == bfmt == cfmt == "f32":
                    name = "msf32_fma"
                else:
                    name = "msf32_fma_%s_%s_%s" % (afmt, bfmt, cfmt)
                for idx, (i, j, k) in enumerate(FMA_TRIPLES):
                    rms = RMS4 if idx < 12 else ["te"]
                    for rm in rms:
                        args = [POOLS[afmt][i], POOLS[bfmt][j], POOLS[cfmt][k]]
                        r, f = ref_fma(afmt, args[0], bfmt, args[1],
                                       cfmt, args[2], rm)
                        out.append(vline(name, rm, args, r, f, prov))
    for sfmt in ("f32", "f64"):
        name = "msf32_sqrt" if sfmt == "f32" else "msf32_sqrt_f64"
        extra = [enc_exact_frac(sfmt, Fraction(2)),
                 enc_exact_frac(sfmt, Fraction(1, 4)),
                 enc_exact_frac(sfmt, Fraction(9)),
                 enc_exact_frac(sfmt, Fraction(2) ** 40 if sfmt == "f64" else Fraction(2) ** 20)]
        for a in POOLS[sfmt] + extra:
            for rm in RMS4:
                r, f = ref_sqrt(sfmt, a, rm)
                out.append(vline(name, rm, [a], r, f, prov))
    return out


def gen_conv_int(prov):
    out = []
    for sfmt in ("f32", "f64"):
        name = "msf32_from_%s" % sfmt
        for a in POOLS[sfmt]:
            for rm in RMS4:
                r, f = ref_conv(sfmt, a, rm)
                out.append(vline(name, rm, [a], r, f, prov))
    candidates = [0, 1, -1, 2, -2, 3, 127, -128, 255, 256, -129, 32767,
                  -32768, 65535, 65536, (1 << 24) - 1, 1 << 24, (1 << 24) + 1,
                  -(1 << 24), (1 << 31) - 1, -(1 << 31), (1 << 32) - 1,
                  1 << 53, (1 << 53) + 2, (1 << 63) - 1, -(1 << 63),
                  (1 << 64) - 1, 123456789, -987654321]
    for tok, (is_signed, width) in INT_KINDS.items():
        lo = -(1 << (width - 1)) if is_signed else 0
        hi = (1 << (width - 1)) - 1 if is_signed else (1 << width) - 1
        mask = (1 << width) - 1
        for v in candidates:
            if not (lo <= v <= hi):
                continue
            for rm in RMS4:
                r, f = ref_from_int(v, rm)
                out.append(vline("msf32_from_%s" % tok, rm, [v & mask],
                                 r, f, prov))
    return out


TOINT_VALS = [Fraction(0), Fraction(1, 2), Fraction(-1, 2), Fraction(3, 2),
              Fraction(-3, 2), Fraction(5, 2), Fraction(-5, 2),
              Fraction(2, 5), Fraction(-2, 5), Fraction(3, 5), Fraction(-3, 5),
              Fraction(255, 2), Fraction(-257, 2), Fraction(511, 2),
              Fraction(65535, 2), Fraction(-65537, 2), Fraction(131071, 2),
              Fraction(2) ** 31, -(Fraction(2) ** 31), Fraction(2) ** 32,
              Fraction(2) ** 63, -(Fraction(2) ** 63), Fraction(2) ** 64,
              Fraction(100), Fraction(-100)]


def gen_toint(prov):
    out = []
    inputs = [pack_signed(v, "te", "f32")[0] for v in TOINT_VALS]
    inputs += [POOL32[i] for i in (1, 16, 17, 22, 23, 24, 26, 2)]
    for tok in INT_KINDS:
        for suffix, mode, exact_form in INT_MODES:
            name = "msf32_to_%s_%s" % (tok, suffix)
            for a in inputs:
                r, f = ref_to_int(a, tok, mode, exact_form)
                out.append(vline(name, "-", [a], r, f, prov))
    return out


RINT_VALS = [Fraction(1, 2), Fraction(-1, 2), Fraction(3, 2), Fraction(-3, 2),
             Fraction(5, 2), Fraction(-5, 2), Fraction(7, 2), Fraction(-7, 2),
             Fraction(2, 5), Fraction(-2, 5), Fraction(2) ** 22 + Fraction(1, 2),
             Fraction(2) ** 23 - Fraction(1, 2)]


def gen_rint_next_scale_logb_rem(prov):
    out = []
    rint_inputs = list(POOL32) + [pack_signed(v, "te", "f32")[0]
                                  for v in RINT_VALS]
    named = [("ties_to_even", "te"), ("ties_to_away", "ta"),
             ("toward_zero", "tz"), ("toward_positive", "tp"),
             ("toward_negative", "tn")]
    for suffix, mode in named:
        for a in rint_inputs:
            r, f = ref_rint(a, mode, 0, "te")
            out.append(vline("msf32_round_to_integral_%s" % suffix, "-",
                             [a], r, f, prov))
    for rm in RMS4:
        for a in rint_inputs:
            r, f = ref_rint(a, "te", 1, rm)
            out.append(vline("msf32_round_to_integral_exact", rm,
                             [a], r, f, prov))
    for a in POOL32:
        for up, nm in ((1, "msf32_next_up"), (0, "msf32_next_down")):
            r, f = ref_next(a, up)
            out.append(vline(nm, "-", [a], r, f, prov))
    for a in POOL32:
        r, f = ref_logb(a)
        out.append(vline("msf32_log_b", "-", [a], r, f, prov))
    # scaleB: x from a subset, N semantic values encoded as binary64
    nvals = [Fraction(0), Fraction(1), Fraction(-1), Fraction(5, 2),
             Fraction(-5, 2), Fraction(1, 2), Fraction(-1, 2), Fraction(127),
             Fraction(-149), Fraction(300), Fraction(-300), Fraction(10) ** 30]
    npool = [pack_signed(v, "te", "f64")[0] for v in nvals]
    c64 = fmt_consts("f64")
    npool += [c64["signbit"], c64["inf"], c64["signbit"] | c64["inf"],
              c64["inf"] | c64["quiet"], c64["inf"] | 1,
              enc_fields("f64", 0, 0, 1)]
    xidx = [0, 1, 2, 3, 5, 7, 8, 13, 16, 17, 22, 23, 24, 26, 4, 30]
    for i in xidx:
        for nb in npool:
            r, f = ref_scaleb(POOL32[i], nb, "te")
            out.append(vline("msf32_scale_b", "te", [POOL32[i], nb],
                             r, f, prov))
    for i in (2, 5, 7, 16, 30, 4):
        for nb in npool[:9]:
            for rm in ("tz", "tp", "tn"):
                r, f = ref_scaleb(POOL32[i], nb, rm)
                out.append(vline("msf32_scale_b", rm, [POOL32[i], nb],
                                 r, f, prov))
    # remainder: pool pairs plus dyadic tie constructions
    for (i, j) in NUM_PAIRS + [(7, 22), (22, 7), (7, 0), (24, 7), (7, 26),
                               (2, 22), (0, 7), (1, 7)]:
        r, f = ref_remainder(POOL32[i], POOL32[j])
        out.append(vline("msf32_remainder", "-", [POOL32[i], POOL32[j]],
                         r, f, prov))
    tie_pairs = [(5, 2), (7, 2), (9, 2), (1, 2), (3, 2), (11, 4), (13, 4),
                 (1, 3), (100, 7), (-5, 2), (5, -2), (-7, -2), (123, 10),
                 (1, 10 ** 6), (10 ** 6, 3)]
    for (xv, yv) in tie_pairs:
        a = enc_exact_frac("f32", Fraction(xv))
        b = enc_exact_frac("f32", Fraction(yv))
        r, f = ref_remainder(a, b)
        out.append(vline("msf32_remainder", "-", [a, b], r, f, prov))
    return out


def gen_compare_total(prov):
    out = []
    pair_idx = [(7, 7), (7, 8), (8, 7), (0, 1), (1, 0), (2, 0), (3, 2),
                (5, 4), (4, 5), (22, 22), (22, 23), (23, 16), (16, 22),
                (7, 22), (24, 7), (7, 24), (26, 26), (24, 25), (27, 7),
                (9, 7), (10, 7), (30, 30), (30, 31), (2, 3), (16, 17),
                (7, 16), (0, 2), (1, 3)]
    homog = [(POOL32[i], POOL32[j]) for (i, j) in pair_idx]
    cross = [(POOL32[i], POOL64[j]) for (i, j) in pair_idx]
    # cross-format equal-value pairs: f32 operand vs its exact widening,
    # and vs the binary64 value one ulp either side of that widening
    for i in (7, 30, 2, 5, 28):
        wide = enc_exact_frac("f64", Dec("f32", POOL32[i]).value())
        cross += [(POOL32[i], wide), (POOL32[i], wide + 1),
                  (POOL32[i], wide - 1)]
    for suffix, relset, signaling in CMP_PREDS:
        for (a, b) in homog:
            r, f = ref_compare("f32", a, "f32", b, relset, signaling)
            out.append(vline("msf32_compare_%s" % suffix, "-", [a, b],
                             r, f, prov))
        for (a, b) in cross:
            r, f = ref_compare("f32", a, "f64", b, relset, signaling)
            out.append(vline("msf32_compare_%s_f64" % suffix, "-", [a, b],
                             r, f, prov))
    to_pool = [POOL32[i] for i in
               (25, 24, 27, 26, 23, 17, 8, 6, 3, 1, 0, 2, 5, 7, 16, 22)]
    to_pool += [POOL32[24] | 1, POOL32[26] + 1,
                POOL32[27] - 1, POOL32[25] - 1]
    for a in to_pool:
        for b in to_pool:
            r, _ = ref_total_order(a, b, 0)
            out.append(vline("msf32_total_order", "-", [a, b], r, None, prov))
            r, _ = ref_total_order(a, b, 1)
            out.append(vline("msf32_total_order_mag", "-", [a, b],
                             r, None, prov))
    return out


def directed(outdir):
    outdir = Path(outdir)
    total = 0
    total += write_file(outdir / "arith-f32.vec",
                        gen_arith("exact-py-f32:directed-arith"))
    total += write_file(outdir / "fma-sqrt-f32.vec",
                        gen_fma_sqrt("exact-py-f32:directed-fma-sqrt"))
    total += write_file(outdir / "conv-int-f32.vec",
                        gen_conv_int("exact-py-f32:directed-conv-int"))
    total += write_file(outdir / "toint-f32.vec",
                        gen_toint("exact-py-f32:directed-toint"))
    total += write_file(outdir / "rint-misc-f32.vec",
                        gen_rint_next_scale_logb_rem(
                            "exact-py-f32:directed-rint-misc"))
    total += write_file(outdir / "compare-f32.vec",
                        gen_compare_total("exact-py-f32:directed-compare"))
    print("directed total bytes: %d" % total)
    return 0


# ---------------- seeded sweep ----------------

def random_bits(rng, fmt):
    c = fmt_consts(fmt)
    t = c["t"]
    r = rng.random()
    if r < 0.08:
        return rng.choice(POOLS[fmt])
    sign = rng.randint(0, 1)
    if r < 0.16:
        return enc_fields(fmt, sign, 0, rng.getrandbits(t))
    if r < 0.26:
        expfield = rng.choice([1, 2, 3, c["expmax"] - 2, c["expmax"] - 1,
                                c["bias"] - 1, c["bias"], c["bias"] + 1])
        frac = rng.choice([0, 1, c["fracmask"], c["quiet"],
                           rng.getrandbits(t)])
        return enc_fields(fmt, sign, expfield, frac)
    if r < 0.30:
        # specials: infinities and NaNs with varied payloads
        frac = rng.choice([0, 1, c["quiet"], c["quiet"] | 1,
                           rng.getrandbits(t), c["fracmask"]])
        return enc_fields(fmt, sign, c["expmax"], frac)
    while True:
        expfield = int(rng.gauss(c["bias"], c["bias"] / 3.0))
        if 1 <= expfield < c["expmax"]:
            break
    frac = rng.choice([rng.getrandbits(t), rng.getrandbits(t),
                       rng.getrandbits(rng.choice([1, 4, 8])),
                       c["fracmask"] - rng.getrandbits(4)])
    return enc_fields(fmt, sign, expfield, frac)


def sweep(outfile, n, seed):
    rng = random.Random(seed)
    prov = "exact-py-f32:sweep-%d" % seed
    templates = []
    for op, _fn in BINOPS:
        for afmt in ("f32", "f64"):
            for bfmt in ("f32", "f64"):
                templates.append(("bin", op, afmt, bfmt))
    templates += [("sqrt", "f32"), ("sqrt", "f64")]
    for afmt in ("f32", "f64"):
        for bfmt in ("f32", "f64"):
            for cfmt in ("f32", "f64"):
                templates.append(("fma", afmt, bfmt, cfmt))
    templates += [("conv", "f32"), ("conv", "f64")]
    binfn = dict(BINOPS)
    out = []
    for i in range(n):
        tpl = templates[i % len(templates)]
        rm = rng.choice(RMS4)
        if tpl[0] == "bin":
            _, op, afmt, bfmt = tpl
            a, b = random_bits(rng, afmt), random_bits(rng, bfmt)
            r, f = binfn[op](afmt, a, bfmt, b, rm)
            out.append(vline(opname_bin(op, afmt, bfmt), rm, [a, b],
                             r, f, prov))
        elif tpl[0] == "sqrt":
            sfmt = tpl[1]
            a = random_bits(rng, sfmt)
            r, f = ref_sqrt(sfmt, a, rm)
            name = "msf32_sqrt" if sfmt == "f32" else "msf32_sqrt_f64"
            out.append(vline(name, rm, [a], r, f, prov))
        elif tpl[0] == "fma":
            _, afmt, bfmt, cfmt = tpl
            a = random_bits(rng, afmt)
            b = random_bits(rng, bfmt)
            cval = random_bits(rng, cfmt)
            r, f = ref_fma(afmt, a, bfmt, b, cfmt, cval, rm)
            if afmt == bfmt == cfmt == "f32":
                name = "msf32_fma"
            else:
                name = "msf32_fma_%s_%s_%s" % (afmt, bfmt, cfmt)
            out.append(vline(name, rm, [a, b, cval], r, f, prov))
        else:
            sfmt = tpl[1]
            a = random_bits(rng, sfmt)
            r, f = ref_conv(sfmt, a, rm)
            out.append(vline("msf32_from_%s" % sfmt, rm, [a], r, f, prov))
    write_file(outfile, out)
    return 0


def main(argv):
    if len(argv) >= 3 and argv[1] == "directed":
        return directed(argv[2])
    if len(argv) >= 5 and argv[1] == "sweep":
        return sweep(argv[2], int(argv[3]), int(argv[4]))
    raise SystemExit("usage: gen_vectors_f32.py directed OUTDIR | "
                     "sweep OUTFILE N SEED")


if __name__ == "__main__":
    sys.exit(main(sys.argv))



