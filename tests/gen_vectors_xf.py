#!/usr/bin/env python3
"""Project-exact references for the Wave 2 cross-format (xf) rows:
binary32/binary64 destinations with at least one binary16 source.

Test code only (SF-0 4.3). Expected values come from exact rational
arithmetic (Fraction) over decoded integers, never from the
implementation and never through hardware types. The reference
computes the EXACT operation on the exact source values and rounds
once to the destination - the same single-rounding contract the
brief makes load-bearing for src/msf32.c and src/msf64.c. The trap
generators below additionally compute named WRONG pipelines
(convert-sources-first, unfused fma, evaluate-at-binary32-then-
widen) purely to prove the committed trap vectors discriminate;
trap expectations always carry the exact answer.

Special-value rules: IEEE 754-2019 Clauses 6 and 7 by number, the
SF-0 2.5 NaN matrix (first signaling operand quieted wins, else
first quiet, else default; payloads map by trailing-field shift,
truncation to zero payload delivers the default quiet NaN), and
Clause 7.5 tininess after rounding judged on the unbounded-
exponent-rounded result (lead ruling 2026-10-26).

Usage:
  gen_vectors_xf.py directed OUTDIR          committed directed sets
  gen_vectors_xf.py sweep OUTFILE N SEED DEST  seeded sweep (f32|f64)
  gen_vectors_xf.py exhaustive-f16 OUTFILE   every f16 encoding into
                                             sqrt_f16 / from_f16, both
                                             dests (build-dir evidence)
"""
import math
import random
import sys
from fractions import Fraction
from pathlib import Path

FLAG_INV, FLAG_DIV0, FLAG_OVF, FLAG_UNF, FLAG_INX = 0x01, 0x02, 0x04, 0x08, 0x10
RMS4 = ["te", "tz", "tp", "tn"]

FMT = {  # name: (bits, precision, exp bits)
    "f16": (16, 11, 5),
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


def _round_q(sign, q, r, den, rm):
    """Increment decision for floor quotient q with remainder r/den."""
    if r == 0:
        return q
    twice = 2 * r
    inc = False
    if rm == "te":
        inc = twice > den or (twice == den and q % 2 == 1)
    elif rm == "tp":
        inc = not sign
    elif rm == "tn":
        inc = bool(sign)
    return q + 1 if inc else q


def pack_mag(sign, mag, rm, fmt):
    """Round exact magnitude Fraction mag once into fmt (Clause 7,
    tininess after rounding, unbounded-exponent judging)."""
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
    q = _round_q(sign, q, r, den, rm)
    if q == (1 << p):
        q >>= 1
        scale += 1
    tiny_u = False
    if e < emin:
        scale_u = e - (p - 1)
        numu, denu = mag.numerator, mag.denominator
        if scale_u >= 0:
            denu <<= scale_u
        else:
            numu <<= -scale_u
        q_u, r_u = divmod(numu, denu)
        q_u = _round_q(sign, q_u, r_u, denu, rm)
        tiny_u = (e + 1 if q_u == (1 << p) else e) < emin
    signbit = c["signbit"] if sign else 0
    flags = (FLAG_INX | (FLAG_UNF if tiny_u else 0)) if inexact else 0
    if q >= (1 << (p - 1)):
        big_e = scale + (p - 1)
        if big_e > emax:
            to_inf = rm == "te" or (rm == "tp" and not sign) \
                or (rm == "tn" and sign)
            enc = c["inf"] if to_inf else ((c["expmax"] - 1) << t) | c["fracmask"]
            return signbit | enc, FLAG_OVF | FLAG_INX
        return signbit | ((big_e + c["bias"]) << t) | (q - (1 << (p - 1))), flags
    return signbit | q, flags


def pack_signed(value, rm, fmt):
    return pack_mag(1 if value < 0 else 0, abs(value), rm, fmt)


def pack_sticky_mag(sign, q, exp, sticky, rm, fmt):
    """Pack a value in [q, q+1) * 2^exp (equal to q*2^exp iff not
    sticky) with q carrying far more than p bits; the midpoint
    substitution cannot cross a rounding boundary."""
    mag = Fraction(2 * q + (1 if sticky else 0), 2)
    if exp >= 0:
        mag *= 1 << exp
    else:
        mag /= 1 << (-exp)
    return pack_mag(sign, mag, rm, fmt)


def zero_bits(fmt, sign):
    return fmt_consts(fmt)["signbit"] if sign else 0


def inf_bits(fmt, sign):
    c = fmt_consts(fmt)
    return (c["signbit"] if sign else 0) | c["inf"]


# ---------------- operation references (dest is f32 or f64) ----------------

def ref_addsub(dest, afmt, a, bfmt, b, issub, rm):
    da, db = Dec(afmt, a), Dec(bfmt, b)
    effb = db.sign ^ (1 if issub else 0)
    inv = da.cls == "inf" and db.cls == "inf" and da.sign != effb
    bits, bad = nan_delivery(dest, [da, db], inv)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    if da.cls == "inf":
        return inf_bits(dest, da.sign), 0
    if db.cls == "inf":
        return inf_bits(dest, effb), 0
    va, vb = da.value(), db.value()
    exact = va - vb if issub else va + vb
    if exact == 0:
        if va == 0 and vb == 0 and da.sign == effb:
            return zero_bits(dest, da.sign), 0
        return zero_bits(dest, 1 if rm == "tn" else 0), 0
    return pack_signed(exact, rm, dest)


def ref_mul(dest, afmt, a, bfmt, b, rm):
    da, db = Dec(afmt, a), Dec(bfmt, b)
    sign = da.sign ^ db.sign
    inv = (da.cls == "zero" and db.cls == "inf") or \
          (da.cls == "inf" and db.cls == "zero")
    bits, bad = nan_delivery(dest, [da, db], inv)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    if da.cls == "inf" or db.cls == "inf":
        return inf_bits(dest, sign), 0
    if da.cls == "zero" or db.cls == "zero":
        return zero_bits(dest, sign), 0
    return pack_signed(da.value() * db.value(), rm, dest)


def ref_div(dest, afmt, a, bfmt, b, rm):
    da, db = Dec(afmt, a), Dec(bfmt, b)
    sign = da.sign ^ db.sign
    inv = (da.cls == "zero" and db.cls == "zero") or \
          (da.cls == "inf" and db.cls == "inf")
    bits, bad = nan_delivery(dest, [da, db], inv)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    if da.cls == "inf":
        return inf_bits(dest, sign), 0
    if db.cls == "inf":
        return zero_bits(dest, sign), 0
    if db.cls == "zero":
        return inf_bits(dest, sign), FLAG_DIV0
    if da.cls == "zero":
        return zero_bits(dest, sign), 0
    return pack_signed(da.value() / db.value(), rm, dest)


def ref_sqrt(dest, afmt, a, rm):
    da = Dec(afmt, a)
    inv = bool(da.sign) and da.cls in ("inf", "finite")
    bits, bad = nan_delivery(dest, [da], inv)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    if da.cls == "inf":
        return inf_bits(dest, 0), 0
    if da.cls == "zero":
        return zero_bits(dest, da.sign), 0
    sig, exp = da.sig, da.exp
    if exp % 2:
        sig <<= 1
        exp -= 1
    shift = 240
    scaled = sig << shift
    q = math.isqrt(scaled)
    return pack_sticky_mag(0, q, exp // 2 - shift // 2,
                           scaled != q * q, rm, dest)


def ref_fma(dest, afmt, a, bfmt, b, cfmt, c, rm):
    da, db, dc = Dec(afmt, a), Dec(bfmt, b), Dec(cfmt, c)
    psign = da.sign ^ db.sign
    prod_zero_inf = (da.cls == "zero" and db.cls == "inf") or \
                    (da.cls == "inf" and db.cls == "zero")
    prod_inf = (da.cls == "inf" and not isnan(db) and db.cls != "zero") or \
               (db.cls == "inf" and not isnan(da) and da.cls != "zero")
    inv = prod_zero_inf or (prod_inf and dc.cls == "inf" and psign != dc.sign)
    extra = FLAG_INV if (prod_zero_inf and dc.cls == "qnan") else 0
    bits, bad = nan_delivery(dest, [da, db, dc], inv)
    if bits is not None:
        return bits, extra | (FLAG_INV if bad else 0)
    if prod_inf:
        return inf_bits(dest, psign), 0
    if dc.cls == "inf":
        return inf_bits(dest, dc.sign), 0
    prod = da.value() * db.value()
    exact = prod + dc.value()
    if exact == 0:
        if prod == 0 and dc.value() == 0 and psign == dc.sign:
            return zero_bits(dest, psign), 0
        return zero_bits(dest, 1 if rm == "tn" else 0), 0
    return pack_signed(exact, rm, dest)


def ref_conv(dest, sfmt, a, rm):
    da = Dec(sfmt, a)
    bits, bad = nan_delivery(dest, [da], False)
    if bits is not None:
        return bits, FLAG_INV if bad else 0
    if da.cls == "inf":
        return inf_bits(dest, da.sign), 0
    if da.cls == "zero":
        return zero_bits(dest, da.sign), 0
    return pack_signed(da.value(), rm, dest)


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


BINOPS = [("add", lambda d, af, a, bf, b, rm: ref_addsub(d, af, a, bf, b, False, rm)),
          ("sub", lambda d, af, a, bf, b, rm: ref_addsub(d, af, a, bf, b, True, rm)),
          ("mul", ref_mul), ("div", ref_div)]
BIN_COMBOS = [("f16", "f16"), ("f16", "f32"), ("f16", "f64"),
              ("f32", "f16"), ("f64", "f16")]
FMA_COMBOS = [(a, b, c) for a in ("f16", "f32", "f64")
              for b in ("f16", "f32", "f64") for c in ("f16", "f32", "f64")
              if "f16" in (a, b, c)]
DESTS = ("f32", "f64")


def all_xf_names():
    names = set()
    for dest in DESTS:
        d = dest[1:]
        for op, _fn in BINOPS:
            for af, bf in BIN_COMBOS:
                names.add("msf%s_%s_%s_%s" % (d, op, af, bf))
        for af, bf, cf in FMA_COMBOS:
            names.add("msf%s_fma_%s_%s_%s" % (d, af, bf, cf))
        names.add("msf%s_sqrt_f16" % d)
        names.add("msf%s_from_f16" % d)
        for suffix, _relset, _sig in CMP_PREDS:
            names.add("msf%s_compare_%s_f16" % (d, suffix))
    return names


# ---------------- operand pools ----------------

def enc_fields(fmt, sign, expfield, frac):
    c = fmt_consts(fmt)
    return (c["signbit"] if sign else 0) | (expfield << c["t"]) | frac


def enc_value(fmt, value):
    """Encode a Fraction that must be exact in fmt."""
    bits, flags = pack_signed(value, "te", fmt)
    d = Dec(fmt, bits)
    assert flags == 0 and d.cls in ("finite", "zero") and d.value() == value, \
        (fmt, value, bits, flags)
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
        enc_value(fmt, Fraction(2)),                    # 11
        enc_value(fmt, Fraction(1, 2)),                 # 12
        enc_value(fmt, Fraction(3, 2)),                 # 13
        enc_value(fmt, Fraction(-3, 2)),                # 14
        enc_value(fmt, Fraction(5, 2)),                 # 15
        maxfinite,                                      # 16 maxfinite
        c["signbit"] | maxfinite,                       # 17 -maxfinite
        enc_value(fmt, Fraction(2) ** (emax - 1)),      # 18 large
        enc_value(fmt, Fraction(2) ** (c["emin"] + 1)),  # 19 tiny normal
        enc_value(fmt, Fraction(3)),                    # 20
        enc_value(fmt, Fraction(-3)),                   # 21
        c["inf"],                                       # 22 +inf
        c["signbit"] | c["inf"],                        # 23 -inf
        c["inf"] | c["quiet"],                          # 24 default qNaN
        c["signbit"] | c["inf"] | c["quiet"] | (0x12345 & c["fracmask"]),  # 25
        c["inf"] | 1,                                   # 26 sNaN payload 1
        c["signbit"] | c["inf"] | (c["quiet"] - 1),     # 27 -sNaN max payload
        enc_value(fmt, Fraction(2) ** c["p"]),          # 28 2^p
        enc_value(fmt, Fraction(2) ** c["p"] - 1),      # 29 2^p - 1
        pack_mag(0, Fraction(1, 10), "te", fmt)[0],     # 30 ~0.1
        pack_mag(1, Fraction(1, 10), "te", fmt)[0],     # 31 ~-0.1
    ]
    assert len(pool) == 32
    return pool


POOLS = {f: make_pool(f) for f in ("f16", "f32", "f64")}


def _extras():
    c16, c32, c64 = (fmt_consts(f) for f in ("f16", "f32", "f64"))
    e16 = [
        enc_fields("f16", 0, 0, 2), enc_fields("f16", 0, 0, 3),
        enc_fields("f16", 1, 0, 0x200), enc_fields("f16", 0, 0, 0x3fe),
        enc_fields("f16", 0, 1, 1), enc_fields("f16", 1, 1, 0x3ff),
        c16["inf"] | c16["quiet"] | 1, c16["inf"] | c16["quiet"] | 0x1ff,
        c16["inf"] | 0x100, c16["signbit"] | c16["inf"] | 1,
        enc_value("f16", Fraction(1, 3) * 3), enc_value("f16", Fraction(2) ** -20),
        enc_value("f16", Fraction(65504)), enc_value("f16", Fraction(1) + Fraction(1, 1024)),
    ]
    e32 = [
        enc_fields("f32", 0, 0, 0x400000), enc_fields("f32", 1, 0, 0x7fffff),
        enc_value("f32", Fraction(2) ** -140), enc_value("f32", Fraction(65520)),
        enc_value("f32", Fraction(2) ** 16), enc_value("f32", Fraction(2) ** -24),
        c32["inf"] | c32["quiet"] | 1, c32["inf"] | 0x200,
        enc_value("f32", Fraction(3, 4)), enc_value("f32", Fraction(-7, 8)),
    ]
    e64 = [
        enc_value("f64", Fraction(2) ** -150),   # half of f32 min subnormal
        enc_value("f64", Fraction(2) ** -149),   # f32 min subnormal, exact
        enc_value("f64", Fraction(1) + Fraction(1, 2 ** 24)),   # f32 tie at 1
        enc_value("f64", Fraction(1) + Fraction(1, 2 ** 24) - Fraction(1, 2 ** 52)),
        enc_value("f64", Fraction(1) + Fraction(1, 2 ** 24) + Fraction(1, 2 ** 52)),
        enc_value("f64", Fraction(2) ** 128),    # above f32 range
        enc_value("f64", Fraction(2) ** -140),
        enc_value("f64", Fraction(65520)), enc_value("f64", Fraction(2) ** 16),
        # NaN payloads around the f64->f32 truncation threshold (2^29):
        c64["inf"] | 1, c64["inf"] | ((1 << 29) - 1), c64["inf"] | (1 << 29),
        c64["inf"] | c64["quiet"] | 1, c64["inf"] | c64["quiet"] | (1 << 29),
        c64["signbit"] | c64["inf"] | ((1 << 29) - 1),
        c64["signbit"] | c64["inf"] | c64["quiet"] | (1 << 28),
    ]
    return {"f16": e16, "f32": e32, "f64": e64}


EXTRAS = _extras()


def vline(op, rm, args, result, flags, prov):
    return "%s %s %s -> %x %02x %s" % (
        op, rm, " ".join("%x" % a for a in args), result, flags, prov)


HDR = "# generated by tests/gen_vectors_xf.py - do not edit (regenerate)\n"


def write_file(path, lines):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    data = HDR + "\n".join(lines) + "\n"
    Path(path).write_bytes(data.encode("utf-8"))
    print("wrote %s (%d lines, %d bytes)" % (path, len(lines), len(data)))
    return len(data)


SPECIAL_IDX = [0, 1, 2, 3, 7, 8, 22, 24, 26, 27]
NUM_PAIRS = [(7, 8), (8, 7), (9, 10), (10, 9), (4, 2), (5, 4),
             (16, 16), (2, 2), (13, 14), (28, 7), (30, 30), (16, 7)]


def gen_arith(prov):
    out = []
    for dest in DESTS:
        for op, fn in BINOPS:
            for afmt, bfmt in BIN_COMBOS:
                name = "msf%s_%s_%s_%s" % (dest[1:], op, afmt, bfmt)
                pa, pb = POOLS[afmt], POOLS[bfmt]
                for i in SPECIAL_IDX:
                    for j in SPECIAL_IDX:
                        r, f = fn(dest, afmt, pa[i], bfmt, pb[j], "te")
                        out.append(vline(name, "te", [pa[i], pb[j]], r, f, prov))
                for (i, j) in NUM_PAIRS:
                    for rm in RMS4:
                        r, f = fn(dest, afmt, pa[i], bfmt, pb[j], rm)
                        out.append(vline(name, rm, [pa[i], pb[j]], r, f, prov))
    # Focused extras for dest f32: f64 tie-zone values and NaN
    # payloads at the f64->f32 truncation threshold, plus f16 NaN
    # payload widening, always against a finite f16 other operand.
    one16 = POOLS["f16"][7]
    for op, fn in BINOPS[:3]:
        for a in EXTRAS["f64"]:
            for combo in (("f64", "f16"), ("f16", "f64")):
                name = "msf32_%s_%s_%s" % (op, combo[0], combo[1])
                args = [a, one16] if combo[0] == "f64" else [one16, a]
                r, f = fn("f32", combo[0], args[0], combo[1], args[1], "te")
                out.append(vline(name, "te", args, r, f, prov))
    for dest in DESTS:
        for b in EXTRAS["f16"]:
            r, f = ref_addsub(dest, "f16", one16, "f16", b, False, "te")
            out.append(vline("msf%s_add_f16_f16" % dest[1:], "te",
                             [one16, b], r, f, prov))
    return out


FMA_TRIPLES = [
    (7, 7, 8), (7, 7, 7), (0, 22, 24), (22, 0, 24), (0, 22, 7), (22, 7, 23),
    (22, 7, 22), (7, 7, 22), (2, 2, 2), (16, 11, 0), (16, 7, 17), (13, 13, 14),
    (28, 7, 8), (9, 9, 10), (30, 30, 31), (5, 12, 2), (4, 11, 3), (24, 7, 7),
    (7, 26, 7), (7, 7, 27), (0, 7, 0), (1, 7, 0), (1, 8, 1), (20, 20, 21),
    (12, 12, 12), (18, 11, 17), (19, 12, 19), (29, 7, 29), (15, 11, 14),
    (6, 7, 5), (3, 11, 2), (10, 10, 8), (31, 31, 30), (25, 26, 24),
    (22, 22, 22), (0, 0, 23), (26, 7, 24), (7, 7, 26),
]


def gen_fma_sqrt(prov):
    out = []
    for dest in DESTS:
        for afmt, bfmt, cfmt in FMA_COMBOS:
            name = "msf%s_fma_%s_%s_%s" % (dest[1:], afmt, bfmt, cfmt)
            for idx, (i, j, k) in enumerate(FMA_TRIPLES):
                rms = RMS4 if idx < 6 else ["te"]
                for rm in rms:
                    args = [POOLS[afmt][i], POOLS[bfmt][j], POOLS[cfmt][k]]
                    r, f = ref_fma(dest, afmt, args[0], bfmt, args[1],
                                   cfmt, args[2], rm)
                    out.append(vline(name, rm, args, r, f, prov))
        name = "msf%s_sqrt_f16" % dest[1:]
        squares = [enc_value("f16", Fraction(v * v))
                   for v in (1, 2, 3, 5, 11, 100)]
        squares += [enc_value("f16", Fraction(1, 4)),
                    enc_value("f16", Fraction(9, 16))]
        for a in POOLS["f16"] + EXTRAS["f16"] + squares:
            for rm in RMS4:
                r, f = ref_sqrt(dest, "f16", a, rm)
                out.append(vline(name, rm, [a], r, f, prov))
    return out


def gen_conv(prov):
    out = []
    for dest in DESTS:
        name = "msf%s_from_f16" % dest[1:]
        for a in POOLS["f16"] + EXTRAS["f16"]:
            for rm in RMS4:
                r, f = ref_conv(dest, "f16", a, rm)
                out.append(vline(name, rm, [a], r, f, prov))
    return out


def gen_compare(prov):
    out = []
    pair_idx = [(7, 7), (7, 8), (8, 7), (0, 1), (1, 0), (2, 0), (3, 2),
                (5, 4), (4, 5), (22, 22), (22, 23), (23, 16), (16, 22),
                (7, 22), (24, 7), (7, 24), (26, 26), (24, 25), (27, 7),
                (9, 7), (10, 7), (30, 30), (2, 3), (16, 17), (0, 2)]
    for dest in DESTS:
        pairs = [(POOLS[dest][i], POOLS["f16"][j]) for (i, j) in pair_idx]
        # equal-value cross pairs: dest operand is the exact widening of
        # the f16 operand, and one dest ulp either side of it
        for j in (2, 5, 7, 16, 30):
            wide = enc_value(dest, Dec("f16", POOLS["f16"][j]).value())
            pairs += [(wide, POOLS["f16"][j]), (wide + 1, POOLS["f16"][j]),
                      (wide - 1, POOLS["f16"][j])]
        # NaN payload positions: f16 NaN extras as second operand
        for b in EXTRAS["f16"][6:10]:
            pairs.append((POOLS[dest][7], b))
        pairs.append((EXTRAS[dest][6] if dest == "f32" else EXTRAS[dest][12],
                      POOLS["f16"][7]))
        for suffix, relset, signaling in CMP_PREDS:
            name = "msf%s_compare_%s_f16" % (dest[1:], suffix)
            for (a, b) in pairs:
                r, f = ref_compare(dest, a, "f16", b, relset, signaling)
                out.append(vline(name, "-", [a, b], r, f, prov))
    return out


# ---------------- double-rounding traps ----------------
# Trap expectations are the EXACT (single-rounding) answers. The
# wrong pipelines exist only to select discriminating operands;
# a case is kept only when the wrong pipeline's result BITS differ.
# Inputs are restricted to finite values so traps test rounding,
# never NaN policy.

def _finite(fmt, bits):
    return Dec(fmt, bits).cls in ("finite", "zero")


def _danger64(rng):
    """f64 encodings in the f32 double-rounding danger zone: the bit
    at the f32 guard position set, tiny or zero sticky below it."""
    out = []
    tops = [1 << 23, (1 << 23) + 1, (1 << 24) - 1, 0xC00000, 0xAAAAAB]
    lows = [0, 1, 2, 1 << 27, (1 << 28) - 1]
    for sign in (0, 1):
        for top in tops:
            for low in lows:
                sig = (top << 29) | (1 << 28) | low
                for e in (0, -1, 1, -126, -127, -140, 126, 127):
                    v = Fraction(sig) * Fraction(2) ** (e - 52)
                    out.append(enc_value("f64", -v if sign else v))
    rng.shuffle(out)
    return out


def _near_one(fmt):
    out = []
    kmax = {"f16": 10, "f32": 23, "f64": 40}[fmt]
    for k in range(1, kmax + 1):
        out.append(enc_value(fmt, Fraction(1) + Fraction(1, 2 ** k)))
        out.append(enc_value(fmt, Fraction(1) - Fraction(1, 2 ** (k + 1))))
    return out


def _small16():
    vals = [POOLS["f16"][i] for i in (2, 5, 7, 9, 10, 12, 13, 30)]
    vals += [enc_value("f16", Fraction(1, 2 ** k)) for k in (1, 4, 8, 12, 16, 20)]
    vals += [enc_value("f16", -Fraction(1, 2 ** k)) for k in (1, 8, 16)]
    return vals


def _wf_convert_first_bin(fn, afmt, a, bfmt, b, rm):
    a2, _ = ref_conv("f32", afmt, a, rm)
    b2, _ = ref_conv("f32", bfmt, b, rm)
    return fn("f32", "f32", a2, "f32", b2, rm)


def _wf_convert_first_fma(afmt, a, bfmt, b, cfmt, c, rm):
    a2, _ = ref_conv("f32", afmt, a, rm)
    b2, _ = ref_conv("f32", bfmt, b, rm)
    c2, _ = ref_conv("f32", cfmt, c, rm)
    return ref_fma("f32", "f32", a2, "f32", b2, "f32", c2, rm)


def _wf_unfused(dest, afmt, a, bfmt, b, cfmt, c, rm):
    p, _ = ref_mul(dest, afmt, a, bfmt, b, rm)
    return ref_addsub(dest, dest, p, cfmt, c, False, rm)


def _wf_via_f32_bin(fn, afmt, a, bfmt, b, rm):
    r32, _ = fn("f32", afmt, a, bfmt, b, rm)
    return ref_conv("f64", "f32", r32, rm)


def _wf_via_f32_fma(afmt, a, bfmt, b, cfmt, c, rm):
    r32, _ = ref_fma("f32", afmt, a, bfmt, b, cfmt, c, rm)
    return ref_conv("f64", "f32", r32, rm)


def _trap_search(candidates, exact_fn, wrong_fn, quota):
    """candidates: iterable of (name, rm, args). Returns kept tuples
    (name, rm, args, bits, flags) with exact expectations."""
    kept, per_name = [], {}
    for name, rm, args in candidates:
        if per_name.get(name, 0) >= quota:
            continue
        eb, ef = exact_fn(rm, args)
        wb, _wf = wrong_fn(rm, args)
        if eb != wb:
            kept.append((name, rm, args, eb, ef))
            per_name[name] = per_name.get(name, 0) + 1
    return kept


def gen_traps():
    rng = random.Random(20261027)
    danger = _danger64(rng)
    small16 = _small16()
    near1 = {f: _near_one(f) for f in ("f16", "f32", "f64")}
    binfn = dict(BINOPS)
    out = []
    counts = {}

    def emit(kept, prov, family, dest):
        for (name, rm, args, bits, flags) in kept:
            out.append(vline(name, rm, args, bits, flags, prov))
        counts[(prov, family, dest)] = counts.get((prov, family, dest), 0) + len(kept)

    # dest f32: convert-sources-to-f32-first (f64-bearing rows only;
    # f16/f32 sources convert exactly, so those rows have no trap)
    for op, fn in BINOPS:
        for afmt, bfmt in (("f16", "f64"), ("f64", "f16")):
            name = "msf32_%s_%s_%s" % (op, afmt, bfmt)
            def cand(afmt=afmt, bfmt=bfmt, name=name):
                pa = danger if afmt == "f64" else small16
                pb = danger if bfmt == "f64" else small16
                for ia, a in enumerate(pa):
                    for ib, b in enumerate(pb):
                        yield name, RMS4[(ia + ib) % 4], (afmt, a, bfmt, b)
            kept = _trap_search(
                cand(),
                lambda rm, t, fn=fn: fn("f32", t[0], t[1], t[2], t[3], rm),
                lambda rm, t, fn=fn: _wf_convert_first_bin(fn, t[0], t[1], t[2], t[3], rm),
                3)
            kept = [(n, rm, [t[1], t[3]], b, f) for (n, rm, t, b, f) in kept]
            emit(kept, "exact-py-xf:trap-convert-first", op, "f32")
    # dest f32 fma: convert-first on f64-and-f16-bearing triples
    pos_pool = {"f16": small16, "f32": [POOLS["f32"][i] for i in (7, 9, 10, 13, 30)],
                "f64": danger}
    for afmt, bfmt, cfmt in FMA_COMBOS:
        if "f64" not in (afmt, bfmt, cfmt):
            continue
        name = "msf32_fma_%s_%s_%s" % (afmt, bfmt, cfmt)
        def cand(afmt=afmt, bfmt=bfmt, cfmt=cfmt, name=name):
            for ia, a in enumerate(pos_pool[afmt][:60]):
                for ib, b in enumerate(pos_pool[bfmt][:12]):
                    for ic, c in enumerate(pos_pool[cfmt][:12]):
                        yield name, RMS4[(ia + ib + ic) % 4], (afmt, a, bfmt, b, cfmt, c)
        kept = _trap_search(
            cand(),
            lambda rm, t: ref_fma("f32", t[0], t[1], t[2], t[3], t[4], t[5], rm),
            lambda rm, t: _wf_convert_first_fma(t[0], t[1], t[2], t[3], t[4], t[5], rm),
            2)
        kept = [(n, rm, [t[1], t[3], t[5]], b, f) for (n, rm, t, b, f) in kept]
        emit(kept, "exact-py-xf:trap-convert-first", "fma", "f32")
    # both dests: unfused mul-then-add. Construction family in
    # integer form at dest precision p: A = (2^ka + 1) * 2^S,
    # B = (2^kb + 1) * 2^S with ka + kb = p give a (p+1)-bit product
    # whose lowest bit sits exactly at the guard position (a tie);
    # C = 2^(2S) then flips the fused result off that tie while the
    # unfused path rounds the product away first.
    # Scaled variants place each factor inside its format. Combos
    # whose exact product always fits the dest precision (such as
    # f16*f16 into f32) provably have no unfused trap and are
    # simply not found; the assert below is per dest, not per combo.
    for dest in DESTS:
        p = fmt_consts(dest)["p"]
        for afmt, bfmt, cfmt in FMA_COMBOS:
            name = "msf%s_fma_%s_%s_%s" % (dest[1:], afmt, bfmt, cfmt)
            def cand(afmt=afmt, bfmt=bfmt, cfmt=cfmt, name=name, p=p):
                for ka in range(1, p):
                    kb = p - ka
                    for s in range(-40, 41, 4):
                        av = Fraction((1 << ka) + 1) * Fraction(2) ** s
                        bv = Fraction((1 << kb) + 1) * Fraction(2) ** s
                        for cv in (Fraction(2) ** (2 * s),
                                   -Fraction(2) ** (2 * s),
                                   Fraction(2) ** (2 * s + 1)):
                            if (_exact_in(afmt, av) and _exact_in(bfmt, bv)
                                    and _exact_in(cfmt, cv)):
                                yield name, "te", (afmt, enc_value(afmt, av),
                                                   bfmt, enc_value(bfmt, bv),
                                                   cfmt, enc_value(cfmt, cv))
                for a in near1[afmt][:24]:
                    for b in near1[bfmt][:24]:
                        yield name, "te", (afmt, a, bfmt, b, cfmt,
                                           POOLS[cfmt][2])
            kept = _trap_search(
                cand(),
                lambda rm, t, dest=dest: ref_fma(dest, t[0], t[1], t[2], t[3], t[4], t[5], rm),
                lambda rm, t, dest=dest: _wf_unfused(dest, t[0], t[1], t[2], t[3], t[4], t[5], rm),
                1)
            kept = [(n, rm, [t[1], t[3], t[5]], b, f) for (n, rm, t, b, f) in kept]
            emit(kept, "exact-py-xf:trap-unfused", "fma", dest)
    # dest f64: evaluate at binary32 then widen, per family
    for op, fn in BINOPS:
        def cand(op=op):
            for afmt, bfmt in BIN_COMBOS:
                name = "msf64_%s_%s_%s" % (op, afmt, bfmt)
                for a in POOLS[afmt] + EXTRAS[afmt]:
                    if not _finite(afmt, a):
                        continue
                    for b in POOLS[bfmt][:20]:
                        if _finite(bfmt, b):
                            yield name, "te", (afmt, a, bfmt, b)
        kept = _trap_search(
            cand(),
            lambda rm, t, fn=fn: fn("f64", t[0], t[1], t[2], t[3], rm),
            lambda rm, t, fn=fn: _wf_via_f32_bin(fn, t[0], t[1], t[2], t[3], rm),
            1)
        kept = [(n, rm, [t[1], t[3]], b, f) for (n, rm, t, b, f) in kept]
        emit(kept, "exact-py-xf:trap-via-f32", op, "f64")
    kept = _trap_search(
        (("msf64_sqrt_f16", "te", (a,)) for a in POOLS["f16"] + EXTRAS["f16"]
         if _finite("f16", a)),
        lambda rm, t: ref_sqrt("f64", "f16", t[0], rm),
        lambda rm, t: ref_conv("f64", "f32", ref_sqrt("f32", "f16", t[0], rm)[0], rm),
        3)
    emit([(n, rm, [t[0]], b, f) for (n, rm, t, b, f) in kept],
         "exact-py-xf:trap-via-f32", "sqrt", "f64")
    def cand_fma64():
        for afmt, bfmt, cfmt in FMA_COMBOS:
            name = "msf64_fma_%s_%s_%s" % (afmt, bfmt, cfmt)
            for (i, j, k) in FMA_TRIPLES:
                a, b, c = POOLS[afmt][i], POOLS[bfmt][j], POOLS[cfmt][k]
                if _finite(afmt, a) and _finite(bfmt, b) and _finite(cfmt, c):
                    yield name, "te", (afmt, a, bfmt, b, cfmt, c)
    kept = _trap_search(
        cand_fma64(),
        lambda rm, t: ref_fma("f64", t[0], t[1], t[2], t[3], t[4], t[5], rm),
        lambda rm, t: _wf_via_f32_fma(t[0], t[1], t[2], t[3], t[4], t[5], rm),
        1)
    emit([(n, rm, [t[1], t[3], t[5]], b, f) for (n, rm, t, b, f) in kept],
         "exact-py-xf:trap-via-f32", "fma", "f64")

    for key in sorted(counts):
        print("traps %s %s dest=%s: %d" % (key[0], key[1], key[2], counts[key]))
    for fam in ("add", "sub", "mul", "div", "fma"):
        assert counts.get(("exact-py-xf:trap-convert-first", fam, "f32"), 0) >= 1, fam
        assert counts.get(("exact-py-xf:trap-via-f32", fam, "f64"), 0) >= 1, fam
    for dest in DESTS:
        assert counts.get(("exact-py-xf:trap-unfused", "fma", dest), 0) >= 1, dest
    assert counts.get(("exact-py-xf:trap-via-f32", "sqrt", "f64"), 0) >= 1
    return out


def _exact_in(fmt, value):
    bits, flags = pack_signed(value, "te", fmt)
    d = Dec(fmt, bits)
    return flags == 0 and d.cls in ("finite", "zero") and d.value() == value


def proof_convert_first_f64():
    """Sampled check of the theorem the lead ruling rests on:
    converting sources to f64 first is exact, hence cannot differ
    from exact-then-round for dest f64. Returns cases checked."""
    checked = 0
    for op, fn in BINOPS:
        for afmt, bfmt in BIN_COMBOS:
            for i in SPECIAL_IDX:
                for j in SPECIAL_IDX:
                    a, b = POOLS[afmt][i], POOLS[bfmt][j]
                    if isnan(Dec(afmt, a)) or isnan(Dec(bfmt, b)):
                        continue
                    exact = fn("f64", afmt, a, bfmt, b, "te")
                    a2, _ = ref_conv("f64", afmt, a, "te")
                    b2, _ = ref_conv("f64", bfmt, b, "te")
                    conv = fn("f64", "f64", a2, "f64", b2, "te")
                    assert exact == conv, (op, afmt, a, bfmt, b, exact, conv)
                    checked += 1
    for afmt, bfmt, cfmt in FMA_COMBOS:
        for (i, j, k) in FMA_TRIPLES[:12]:
            a, b, c = POOLS[afmt][i], POOLS[bfmt][j], POOLS[cfmt][k]
            if isnan(Dec(afmt, a)) or isnan(Dec(bfmt, b)) or isnan(Dec(cfmt, c)):
                continue
            exact = ref_fma("f64", afmt, a, bfmt, b, cfmt, c, "te")
            a2, _ = ref_conv("f64", afmt, a, "te")
            b2, _ = ref_conv("f64", bfmt, b, "te")
            c2, _ = ref_conv("f64", cfmt, c, "te")
            conv = ref_fma("f64", "f64", a2, "f64", b2, "f64", c2, "te")
            assert exact == conv, (afmt, a, bfmt, b, cfmt, c)
            checked += 1
    print("convert-first-to-f64 sampled proof: %d cases, 0 differences" % checked)
    return checked


def directed(outdir):
    outdir = Path(outdir)
    total = 0
    total += write_file(outdir / "arith-xf.vec",
                        gen_arith("exact-py-xf:directed-arith"))
    total += write_file(outdir / "fma-sqrt-xf.vec",
                        gen_fma_sqrt("exact-py-xf:directed-fma-sqrt"))
    total += write_file(outdir / "conv-xf.vec",
                        gen_conv("exact-py-xf:directed-conv"))
    total += write_file(outdir / "compare-xf.vec",
                        gen_compare("exact-py-xf:directed-compare"))
    nproof = proof_convert_first_f64()
    traps = ["# convert-first-to-f64 sampled proof at generation: "
             "%d cases, 0 differences (lead ruling in ledger)" % nproof]
    traps += gen_traps()
    total += write_file(outdir / "traps-xf.vec", traps)
    seen = set()
    for f in ("arith-xf.vec", "fma-sqrt-xf.vec", "conv-xf.vec",
              "compare-xf.vec", "traps-xf.vec"):
        for line in (outdir / f).read_text(encoding="utf-8").splitlines():
            if line and not line.startswith("#"):
                seen.add(line.split()[0])
    missing = all_xf_names() - seen
    assert not missing, sorted(missing)
    print("directed: all %d xf instantiations present; total %d bytes"
          % (len(seen & all_xf_names()), total))
    assert total < 1000000, total
    return 0


# ---------------- seeded sweep ----------------

def random_bits(rng, fmt):
    c = fmt_consts(fmt)
    t = c["t"]
    r = rng.random()
    if r < 0.08:
        return rng.choice(POOLS[fmt] + EXTRAS[fmt])
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
        frac = rng.choice([0, 1, c["quiet"], c["quiet"] | 1,
                           rng.getrandbits(t), c["fracmask"]])
        return enc_fields(fmt, sign, c["expmax"], frac)
    if fmt == "f64" and r < 0.38:
        # danger-zone significands for cross-format rounding stress
        top = (1 << 23) | rng.getrandbits(23)
        sig = (top << 29) | (1 << 28) | rng.choice([0, 1, 2, 3, 1 << 27])
        e = rng.choice([0, -1, 1, -126, -140, 127, -24, 24])
        v = Fraction(sig) * Fraction(2) ** (e - 52)
        return enc_value("f64", -v if sign else v)
    while True:
        expfield = int(rng.gauss(c["bias"], c["bias"] / 3.0))
        if 1 <= expfield < c["expmax"]:
            break
    frac = rng.choice([rng.getrandbits(t), rng.getrandbits(t),
                       rng.getrandbits(rng.choice([1, 4, 8])),
                       c["fracmask"] - rng.getrandbits(4)])
    return enc_fields(fmt, sign, expfield, frac)


def sweep(outfile, n, seed, dest):
    rng = random.Random(seed)
    prov = "exact-py-xf:sweep-%d" % seed
    templates = []
    for op, _fn in BINOPS:
        for afmt, bfmt in BIN_COMBOS:
            templates.append(("bin", op, afmt, bfmt))
    for afmt, bfmt, cfmt in FMA_COMBOS:
        templates.append(("fma", afmt, bfmt, cfmt))
    templates.append(("sqrt",))
    templates.append(("conv",))
    for suffix, _relset, _sig in CMP_PREDS:
        templates.append(("cmp", suffix))
    binfn = dict(BINOPS)
    cmpmap = {s: (relset, sig) for s, relset, sig in CMP_PREDS}
    out = []
    for i in range(n):
        tpl = templates[i % len(templates)]
        rm = rng.choice(RMS4)
        if tpl[0] == "bin":
            _, op, afmt, bfmt = tpl
            a, b = random_bits(rng, afmt), random_bits(rng, bfmt)
            r, f = binfn[op](dest, afmt, a, bfmt, b, rm)
            name = "msf%s_%s_%s_%s" % (dest[1:], op, afmt, bfmt)
            out.append(vline(name, rm, [a, b], r, f, prov))
        elif tpl[0] == "fma":
            _, afmt, bfmt, cfmt = tpl
            a = random_bits(rng, afmt)
            b = random_bits(rng, bfmt)
            cval = random_bits(rng, cfmt)
            r, f = ref_fma(dest, afmt, a, bfmt, b, cfmt, cval, rm)
            name = "msf%s_fma_%s_%s_%s" % (dest[1:], afmt, bfmt, cfmt)
            out.append(vline(name, rm, [a, b, cval], r, f, prov))
        elif tpl[0] == "sqrt":
            a = random_bits(rng, "f16")
            r, f = ref_sqrt(dest, "f16", a, rm)
            out.append(vline("msf%s_sqrt_f16" % dest[1:], rm, [a], r, f, prov))
        elif tpl[0] == "conv":
            a = random_bits(rng, "f16")
            r, f = ref_conv(dest, "f16", a, rm)
            out.append(vline("msf%s_from_f16" % dest[1:], rm, [a], r, f, prov))
        else:
            relset, sig = cmpmap[tpl[1]]
            a = random_bits(rng, dest)
            b = random_bits(rng, "f16")
            r, f = ref_compare(dest, a, "f16", b, relset, sig)
            name = "msf%s_compare_%s_f16" % (dest[1:], tpl[1])
            out.append(vline(name, "-", [a, b], r, f, prov))
    write_file(outfile, out)
    return 0


def exhaustive_f16(outfile):
    prov = "exact-py-xf:exhaustive-f16-unary"
    out = []
    for bits in range(65536):
        for dest in DESTS:
            r, f = ref_conv(dest, "f16", bits, "te")
            out.append(vline("msf%s_from_f16" % dest[1:], "te", [bits], r, f, prov))
            for rm in ("te", "tp", "tn"):
                r, f = ref_sqrt(dest, "f16", bits, rm)
                out.append(vline("msf%s_sqrt_f16" % dest[1:], rm, [bits], r, f, prov))
    write_file(outfile, out)
    return 0


def main(argv):
    if len(argv) >= 3 and argv[1] == "directed":
        return directed(argv[2])
    if len(argv) >= 6 and argv[1] == "sweep":
        return sweep(argv[2], int(argv[3]), int(argv[4]), argv[5])
    if len(argv) >= 3 and argv[1] == "exhaustive-f16":
        return exhaustive_f16(argv[2])
    raise SystemExit("usage: gen_vectors_xf.py directed OUTDIR | "
                     "sweep OUTFILE N SEED DEST | exhaustive-f16 OUTFILE")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
