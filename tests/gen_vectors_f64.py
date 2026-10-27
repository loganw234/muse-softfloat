#!/usr/bin/env python3
"""Project-exact binary64 references and vectors (parcel-f64).

Independent exact references for the wave-1 msf64_ instantiations:
operand decode from the interchange fields, exact values as
Fraction, and a from-first-principles round-and-pack for the
destination format (tininess after rounding, SF-0 Section 2.5).
NaN delivery follows the project matrix recorded in
src/msf_decode.h; integer-conversion saturation follows the public
header rule; scaleB truncates a non-integral exponent operand
toward zero (project ruling for the language-defined case).

Usage:
  gen_vectors_f64.py directed OUTDIR     committed directed sets
  gen_vectors_f64.py sweep OUTFILE N SEED  seeded cross-format sweep
"""
import random
import sys
from fractions import Fraction
from math import isqrt
from pathlib import Path

FMTS = {"f32": (32, 24, 8), "f64": (64, 53, 11)}
F_INV = 0x01
F_DIV0 = 0x02
F_OVF = 0x04
F_UNF = 0x08
F_INX = 0x10
RMS = ["te", "tz", "tp", "tn"]


def fmt_params(fmt):
    bits, p, w = FMTS[fmt]
    t = bits - 1 - w
    emax = (1 << (w - 1)) - 1
    return bits, p, w, t, emax, 1 - emax


def decode(fmt, x):
    bits, p, w, t, emax, emin = fmt_params(fmt)
    sign = (x >> (bits - 1)) & 1
    efield = (x >> t) & ((1 << w) - 1)
    frac = x & ((1 << t) - 1)
    if efield == (1 << w) - 1:
        cls = "inf" if frac == 0 else ("qnan" if frac >> (t - 1) else "snan")
        return dict(sign=sign, cls=cls, sig=frac, exp=0, frac=frac, bits=x)
    if efield == 0:
        cls = "zero" if frac == 0 else "sub"
        return dict(sign=sign, cls=cls, sig=frac, exp=emin - t,
                    frac=frac, bits=x)
    return dict(sign=sign, cls="norm", sig=frac | (1 << t),
                exp=efield - emax - t, frac=frac, bits=x)


def is_nan(d):
    return d["cls"] in ("qnan", "snan")


def exact(d):
    v = Fraction(d["sig"] << d["exp"], 1) if d["exp"] >= 0 \
        else Fraction(d["sig"], 1 << (-d["exp"]))
    return -v if d["sign"] else v


def default_qnan(fmt):
    bits, p, w, t, emax, emin = fmt_params(fmt)
    return (((1 << w) - 1) << t) | (1 << (t - 1))


def nan_to_dest(dfmt, sfmt, d):
    db, dp, dw, dt, demax, demin = fmt_params(dfmt)
    sb, sp, sw, st_, semax, semin = fmt_params(sfmt)
    payload = d["frac"]
    dpayload = payload << (dt - st_) if dt >= st_ else payload >> (st_ - dt)
    if dpayload == 0:
        return default_qnan(dfmt)
    dpayload |= 1 << (dt - 1)
    return (d["sign"] << (db - 1)) | (((1 << dw) - 1) << dt) | dpayload


def nan_delivery(ops, invalid_without_nan=False, extra_invalid=False):
    """ops: list of (fmt, bits). Returns (bits, flags) or None."""
    decs = [(f, decode(f, b)) for f, b in ops]
    for f, d in decs:
        if d["cls"] == "snan":
            return nan_to_dest("f64", f, d), F_INV
    for f, d in decs:
        if d["cls"] == "qnan":
            return nan_to_dest("f64", f, d), (F_INV if extra_invalid else 0)
    if invalid_without_nan:
        return default_qnan("f64"), F_INV
    return None


def pow2(e):
    return Fraction(1 << e, 1) if e >= 0 else Fraction(1, 1 << (-e))


def floor_log2_frac(m):
    e = m.numerator.bit_length() - m.denominator.bit_length()
    while m < pow2(e):
        e -= 1
    while m >= pow2(e + 1):
        e += 1
    return e


def round_mag_scaled(num, den, rm, sign):
    """Round num/den (non-negative) to an integer magnitude."""
    q, r = divmod(num, den)
    if r == 0:
        return q, False
    if rm == "te":
        inc = (2 * r > den) or (2 * r == den and (q & 1))
    elif rm == "ta":
        inc = 2 * r >= den
    elif rm == "tp":
        inc = not sign
    elif rm == "tn":
        inc = bool(sign)
    else:
        inc = False
    return q + (1 if inc else 0), True


def pack_value(val, rm, fmt="f64", zero_sign=0):
    """Round exact Fraction val into fmt.

    Tininess after rounding per Clause 7.5 as ruled in the ledger:
    the value rounded to p bits as though the exponent range were
    unbounded is compared against 2^emin (not the delivered
    subnormal-rounded value).
    """
    bits, p, w, t, emax, emin = fmt_params(fmt)
    signbit = 1 << (bits - 1)
    if val == 0:
        return (signbit if zero_sign else 0), 0
    sign = 1 if val < 0 else 0
    m = -val if sign else val
    e = floor_log2_frac(m)
    scale = max(e, emin) - (p - 1)
    if scale >= 0:
        num, den = m.numerator, m.denominator << scale
    else:
        num, den = m.numerator << (-scale), m.denominator
    q, inexact = round_mag_scaled(num, den, rm, sign)
    if q == (1 << p):
        q >>= 1
        scale += 1
    rounded = q * pow2(scale)
    maxfinite = (2 - Fraction(1, 1 << (p - 1))) * pow2(emax)
    if rounded > maxfinite:
        to_inf = rm in ("te", "ta") or (rm == "tp" and not sign) \
            or (rm == "tn" and sign)
        expmax = (1 << w) - 1
        enc = (expmax << t) if to_inf else (((expmax - 1) << t)
                                            | ((1 << t) - 1))
        return (signbit if sign else 0) | enc, F_OVF | F_INX
    flags = 0
    if inexact:
        flags |= F_INX
        scale_u = e - (p - 1)
        if scale_u >= 0:
            num_u, den_u = m.numerator, m.denominator << scale_u
        else:
            num_u, den_u = m.numerator << (-scale_u), m.denominator
        q_u, _inexact_u = round_mag_scaled(num_u, den_u, rm, sign)
        if q_u == (1 << p):
            q_u >>= 1
            scale_u += 1
        if q_u * pow2(scale_u) < pow2(emin):
            flags |= F_UNF
    if q >= (1 << (p - 1)):
        enc = ((scale + (p - 1) + emax) << t) | (q - (1 << (p - 1)))
        return (signbit if sign else 0) | enc, flags
    return (signbit if sign else 0) | q, flags


def make_bits(fmt, val):
    """Bits for an exactly representable Fraction value (pool build)."""
    b, fl = pack_value(val, "te", fmt)
    assert fl == 0, (fmt, val, fl)
    return b


def round_to_int_signed(x, mode):
    """Round Fraction x to a mathematical integer per mode name."""
    fl = x.numerator // x.denominator
    rem = x - fl
    if mode == "tz":
        return fl if x >= 0 or rem == 0 else fl + 1
    if mode == "tp":
        return fl + (1 if rem else 0)
    if mode == "tn":
        return fl
    if mode == "ta":
        if x < 0:
            return -round_to_int_signed(-x, "ta")
        return fl + (1 if rem >= Fraction(1, 2) else 0)
    # te
    if rem > Fraction(1, 2) or (rem == Fraction(1, 2) and (fl & 1)):
        return fl + 1
    return fl


def zero_sum_sign(s1, s2, rm):
    return s1 if s1 == s2 else (1 if rm == "tn" else 0)


def inf_bits(sign, fmt="f64"):
    bits, p, w, t, emax, emin = fmt_params(fmt)
    return (sign << (bits - 1)) | (((1 << w) - 1) << t)


def ref_addsub(fa, a, fb, b, is_sub, rm):
    da, db = decode(fa, a), decode(fb, b)
    esign = db["sign"] ^ (1 if is_sub else 0)
    inv = da["cls"] == "inf" and db["cls"] == "inf" and da["sign"] != esign
    nd = nan_delivery([(fa, a), (fb, b)], inv)
    if nd:
        return nd
    if da["cls"] == "inf":
        return inf_bits(da["sign"]), 0
    if db["cls"] == "inf":
        return inf_bits(esign), 0
    va, vb = exact(da), exact(db)
    if is_sub:
        vb = -vb
    v = va + vb
    if v == 0:
        if va == 0 and vb == 0:
            s = zero_sum_sign(da["sign"], esign, rm)
        else:
            s = 1 if rm == "tn" else 0
        return pack_value(v, rm, zero_sign=s)
    return pack_value(v, rm)


def ref_mul(fa, a, fb, b, rm):
    da, db = decode(fa, a), decode(fb, b)
    sign = da["sign"] ^ db["sign"]
    inv = (da["cls"] == "zero" and db["cls"] == "inf") \
        or (da["cls"] == "inf" and db["cls"] == "zero")
    nd = nan_delivery([(fa, a), (fb, b)], inv)
    if nd:
        return nd
    if da["cls"] == "inf" or db["cls"] == "inf":
        return inf_bits(sign), 0
    if da["cls"] == "zero" or db["cls"] == "zero":
        return (sign << 63), 0
    return pack_value(exact(da) * exact(db), rm)


def ref_div(fa, a, fb, b, rm):
    da, db = decode(fa, a), decode(fb, b)
    sign = da["sign"] ^ db["sign"]
    inv = (da["cls"] == "zero" and db["cls"] == "zero") \
        or (da["cls"] == "inf" and db["cls"] == "inf")
    nd = nan_delivery([(fa, a), (fb, b)], inv)
    if nd:
        return nd
    if da["cls"] == "inf":
        return inf_bits(sign), 0
    if db["cls"] == "inf" or da["cls"] == "zero":
        return (sign << 63), 0
    if db["cls"] == "zero":
        return inf_bits(sign), F_DIV0
    return pack_value(exact(da) / exact(db), rm)


def ref_sqrt(fa, a, rm):
    da = decode(fa, a)
    inv = bool(da["sign"]) and da["cls"] != "zero"
    nd = nan_delivery([(fa, a)], inv)
    if nd:
        return nd
    if da["cls"] == "inf":
        return inf_bits(0), 0
    if da["cls"] == "zero":
        return (da["sign"] << 63), 0
    sig, exp = da["sig"], da["exp"]
    shift = 220 - sig.bit_length()
    if (exp - shift) % 2:
        shift -= 1
    n = sig << shift
    q = isqrt(n)
    r = n - q * q
    e2 = (exp - shift) // 2
    if r == 0:
        return pack_value(q * pow2(e2), rm)
    results = {pack_value((q + d) * pow2(e2), rm)
               for d in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))}
    assert len(results) == 1, (fa, a, rm, results)
    return results.pop()


def ref_fma(fa, a, fb, b, fc, c, rm):
    dx, dy, dc = decode(fa, a), decode(fb, b), decode(fc, c)
    ps = dx["sign"] ^ dy["sign"]
    pinv = (dx["cls"] == "zero" and dy["cls"] == "inf") \
        or (dx["cls"] == "inf" and dy["cls"] == "zero")
    pinf = (dx["cls"] == "inf" or dy["cls"] == "inf") \
        and dx["cls"] != "zero" and dy["cls"] != "zero" \
        and not is_nan(dx) and not is_nan(dy)
    inv = pinv or (pinf and dc["cls"] == "inf" and dc["sign"] != ps)
    nd = nan_delivery([(fa, a), (fb, b), (fc, c)], inv,
                      extra_invalid=pinv)
    if nd:
        return nd
    if pinf:
        return inf_bits(ps), 0
    if dc["cls"] == "inf":
        return inf_bits(dc["sign"]), 0
    prod = exact(dx) * exact(dy)
    add = exact(dc)
    v = prod + add
    if v == 0:
        if prod == 0 and add == 0:
            s = zero_sum_sign(ps, dc["sign"], rm)
        else:
            s = 1 if rm == "tn" else 0
        return pack_value(v, rm, zero_sign=s)
    return pack_value(v, rm)


def ref_remainder(a, b):
    dx, dy = decode("f64", a), decode("f64", b)
    inv = dx["cls"] == "inf" or dy["cls"] == "zero"
    nd = nan_delivery([("f64", a), ("f64", b)], inv)
    if nd:
        return nd
    if dy["cls"] == "inf" or dx["cls"] == "zero":
        return a, 0
    x, y = exact(dx), exact(dy)
    n = round_to_int_signed(x / y, "te")
    r = x - n * y
    if r == 0:
        return pack_value(r, "te", zero_sign=dx["sign"])
    bits, fl = pack_value(r, "te")
    assert fl == 0, (a, b, r, fl)
    return bits, fl


MODE_OF_RM = {"te": "te", "tz": "tz", "tp": "tp", "tn": "tn", "ta": "ta"}


def ref_rint(a, mode, exact_form):
    da = decode("f64", a)
    nd = nan_delivery([("f64", a)])
    if nd:
        return nd
    if da["cls"] in ("inf", "zero"):
        return a, 0
    x = exact(da)
    q = round_to_int_signed(x, MODE_OF_RM[mode])
    if q == 0:
        bits, fl = pack_value(Fraction(0), "te", zero_sign=da["sign"])
    else:
        bits, fl = pack_value(Fraction(q), "te")
        assert fl == 0
    if exact_form and q != x:
        fl |= F_INX
    return bits, fl


def ref_next(a, is_up):
    da = decode("f64", a)
    nd = nan_delivery([("f64", a)])
    if nd:
        return nd
    maxfin = 0x7FEFFFFFFFFFFFFF
    if da["cls"] == "inf":
        if is_up:
            return ((0x8000000000000000 | maxfin) if da["sign"] else a), 0
        return (a if da["sign"] else maxfin), 0
    if da["cls"] == "zero":
        return (1 if is_up else 0x8000000000000001), 0
    if not da["sign"]:
        return (a + 1 if is_up else a - 1), 0
    return (a - 1 if is_up else a + 1), 0


def ref_scaleb(a, nb, rm):
    dx, dn = decode("f64", a), decode("f64", nb)
    nd = nan_delivery([("f64", a), ("f64", nb)])
    if nd:
        return nd
    if dx["cls"] in ("zero", "inf") or dn["cls"] == "zero":
        return a, 0
    if dn["cls"] == "inf":
        nint = -5000 if dn["sign"] else 5000
    else:
        nint = int(exact(dn))
        nint = max(-5000, min(5000, nint))
    return pack_value(exact(dx) * pow2(nint), rm)


def ref_logb(a):
    da = decode("f64", a)
    nd = nan_delivery([("f64", a)])
    if nd:
        return nd
    if da["cls"] == "zero":
        return inf_bits(1), F_DIV0
    if da["cls"] == "inf":
        return inf_bits(0), 0
    e = floor_log2_frac(abs(exact(da)))
    return pack_value(Fraction(e), "te")


def ref_conv(fa, a, rm):
    da = decode(fa, a)
    nd = nan_delivery([(fa, a)])
    if nd:
        return nd
    if da["cls"] == "inf":
        return inf_bits(da["sign"]), 0
    if da["cls"] == "zero":
        return (da["sign"] << 63), 0
    return pack_value(exact(da), rm)


def ref_from_int(v, rm):
    return pack_value(Fraction(v), rm)


INT_RANGES = {}
for _w in (8, 16, 32, 64):
    INT_RANGES[("i%d" % _w)] = (-(1 << (_w - 1)), (1 << (_w - 1)) - 1, _w)
    INT_RANGES[("u%d" % _w)] = (0, (1 << _w) - 1, _w)


def ref_to_int(a, mode, exact_form, itok):
    da = decode("f64", a)
    lo, hi, w = INT_RANGES[itok]
    mask = (1 << w) - 1
    if is_nan(da):
        return 0, F_INV
    if da["cls"] == "inf":
        v = lo if da["sign"] else hi
        return v & mask, F_INV
    x = exact(da)
    q = round_to_int_signed(x, MODE_OF_RM[mode])
    if q < lo or q > hi:
        v = lo if q < lo else hi
        return v & mask, F_INV
    fl = F_INX if (exact_form and q != x) else 0
    return q & mask, fl


PREDICATES = [
    ("quiet_equal", "eq", 0), ("quiet_not_equal", "ne", 0),
    ("signaling_equal", "eq", 1), ("signaling_not_equal", "ne", 1),
    ("quiet_greater", "gt", 0), ("quiet_greater_equal", "ge", 0),
    ("quiet_less", "lt", 0), ("quiet_less_equal", "le", 0),
    ("quiet_not_greater", "notgt", 0), ("quiet_not_less", "notlt", 0),
    ("quiet_less_unordered", "ltun", 0),
    ("quiet_greater_unordered", "gtun", 0),
    ("quiet_unordered", "unord", 0), ("quiet_ordered", "ord", 0),
    ("signaling_greater", "gt", 1), ("signaling_greater_equal", "ge", 1),
    ("signaling_less", "lt", 1), ("signaling_less_equal", "le", 1),
    ("signaling_not_greater", "notgt", 1),
    ("signaling_not_less", "notlt", 1),
    ("signaling_less_unordered", "ltun", 1),
    ("signaling_greater_unordered", "gtun", 1),
]


def pred_truth(code, rel):
    return {
        "eq": rel == 0, "ne": rel != 0, "gt": rel == 1,
        "ge": rel in (0, 1), "lt": rel == -1, "le": rel in (-1, 0),
        "notgt": rel != 1, "notlt": rel != -1,
        "ltun": rel in (-1, 2), "gtun": rel in (1, 2),
        "unord": rel == 2, "ord": rel != 2,
    }[code]


def ref_compare(fa, a, fb, b, code, signaling):
    da, db = decode(fa, a), decode(fb, b)
    any_nan = is_nan(da) or is_nan(db)
    any_snan = da["cls"] == "snan" or db["cls"] == "snan"
    fl = F_INV if (any_nan if signaling else any_snan) else 0
    if any_nan:
        rel = 2
    elif da["cls"] == "inf" and db["cls"] == "inf":
        rel = 0 if da["sign"] == db["sign"] else (-1 if da["sign"] else 1)
    elif da["cls"] == "inf":
        rel = -1 if da["sign"] else 1
    elif db["cls"] == "inf":
        rel = 1 if db["sign"] else -1
    else:
        va, vb = exact(da), exact(db)
        rel = -1 if va < vb else (1 if va > vb else 0)
    return (1 if pred_truth(code, rel) else 0), fl


def total_key(bits):
    return (~bits) & ((1 << 64) - 1) if bits >> 63 else bits | (1 << 63)


def ref_total(a, b, mag):
    if mag:
        a &= ~(1 << 63)
        b &= ~(1 << 63)
    return (1 if total_key(a) <= total_key(b) else 0), None


def line(op, rm, args, result, flags, prov):
    fl = "--" if flags is None else "%02x" % flags
    return "%s %s %s -> %x %s %s" % (
        op, rm, " ".join("%x" % v for v in args), result, fl, prov)


def pool64():
    fr = Fraction
    vals = [fr(1, 2), fr(1), fr(3, 2), fr(2), fr(3), fr(5), fr(7),
            fr(1, 4), fr(5, 4), fr(2) ** 52, fr(2) ** 53,
            fr(2) ** -100, fr(2) ** 100, fr(2) ** 1023,
            fr(1) + fr(1, 2 ** 52), fr(3, 2) ** 10]
    out = [0, 0x8000000000000000, 1, 0x8000000000000001, 2, 3,
           0x000FFFFFFFFFFFFF, 0x800FFFFFFFFFFFFF,
           0x0010000000000000, 0x8010000000000000,
           0x3FEFFFFFFFFFFFFF, 0xBFEFFFFFFFFFFFFF,
           0x3FF0000000000001, 0x000FFFFFFFFFFFFE,
           0x0010000000000001, 0x7FEFFFFFFFFFFFFF,
           0xFFEFFFFFFFFFFFFF, 0x7FF0000000000000,
           0xFFF0000000000000]
    for v in vals:
        out.append(make_bits("f64", v))
        out.append(make_bits("f64", -v))
    return out


def pool32():
    fr = Fraction
    vals = [fr(1, 2), fr(1), fr(3, 2), fr(2), fr(3), fr(5),
            fr(2) ** 24, fr(2) ** -40, fr(2) ** 60,
            fr(1) + fr(1, 2 ** 23)]
    out = [0, 0x80000000, 1, 0x80000001, 0x007FFFFF, 0x00800000,
           0x7F7FFFFF, 0xFF7FFFFF, 0x7F800000, 0xFF800000]
    for v in vals:
        out.append(make_bits("f32", v))
        out.append(make_bits("f32", -v))
    return out


def nan_pool64():
    return [0x7FF8000000000000, 0xFFF8000000000000,
            0x7FF8000000000001, 0x7FFFFFFFFFFFFFFF,
            0x7FF0000000000001, 0xFFF0000000000001,
            0x7FF4000000000000, 0x7FF0000000001234]


def nan_pool32():
    return [0x7FC00000, 0xFFC00000, 0x7FC00001, 0x7FFFFFFF,
            0x7F800001, 0xFF800001, 0x7FA00000]


HDR = "# generated by tests/gen_vectors_f64.py - do not edit (regenerate)\n"


def write(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HDR + "\n".join(lines) + "\n", encoding="utf-8")
    print("wrote %s (%d lines)" % (path, len(lines)))


def directed_arith(prov):
    out = []
    p64, p32 = pool64(), pool32()
    combos = [("f32", "f32", p32[::4], p32[1::5]),
              ("f32", "f64", p32[::4], p64[1::6]),
              ("f64", "f32", p64[::5], p32[::4]),
              ("f64", "f64", p64[::5], p64[2::6])]
    for fa, fb, pa, pb in combos:
        suf = "" if (fa == "f64" and fb == "f64") else "_%s_%s" % (fa, fb)
        for ia, a in enumerate(pa):
            for ib, b in enumerate(pb):
                pair_modes = (RMS[(ia + ib) % 4], RMS[(ia + ib + 1) % 4])
                for rm in pair_modes:
                    r, f = ref_addsub(fa, a, fb, b, False, rm)
                    out.append(line("msf64_add" + suf, rm, [a, b], r, f, prov))
                    r, f = ref_addsub(fa, a, fb, b, True, rm)
                    out.append(line("msf64_sub" + suf, rm, [a, b], r, f, prov))
                    r, f = ref_mul(fa, a, fb, b, rm)
                    out.append(line("msf64_mul" + suf, rm, [a, b], r, f, prov))
                    r, f = ref_div(fa, a, fb, b, rm)
                    out.append(line("msf64_div" + suf, rm, [a, b], r, f, prov))
    for fa, pa in (("f32", p32), ("f64", p64)):
        suf = "" if fa == "f64" else "_f32"
        for a in pa:
            for rm in RMS:
                r, f = ref_sqrt(fa, a, rm)
                out.append(line("msf64_sqrt" + suf, rm, [a], r, f, prov))
    pools = {"f32": p32[::5], "f64": p64[::6]}
    for fa in ("f32", "f64"):
        for fb in ("f32", "f64"):
            for fc in ("f32", "f64"):
                suf = "" if (fa, fb, fc) == ("f64", "f64", "f64") \
                    else "_%s_%s_%s" % (fa, fb, fc)
                for a in pools[fa]:
                    for b in pools[fb][::2]:
                        for c in pools[fc][1::3]:
                            for rm in ("te", "tn"):
                                r, f = ref_fma(fa, a, fb, b, fc, c, rm)
                                out.append(line("msf64_fma" + suf, rm,
                                                [a, b, c], r, f, prov))
    return out


def directed_conv(prov):
    out = []
    p64, p32 = pool64(), pool32()
    for a in p32 + nan_pool32():
        for rm in RMS:
            r, f = ref_conv("f32", a, rm)
            out.append(line("msf64_from_f32", rm, [a], r, f, prov))
    for a in p64 + nan_pool64():
        for rm in RMS:
            r, f = ref_conv("f64", a, rm)
            out.append(line("msf64_from_f64", rm, [a], r, f, prov))
    intvals = {
        "i8": [-128, -127, -1, 0, 1, 2, 126, 127],
        "u8": [0, 1, 2, 127, 128, 254, 255],
        "i16": [-32768, -32767, -129, -1, 0, 1, 255, 32767],
        "u16": [0, 1, 255, 256, 32768, 65535],
        "i32": [-(1 << 31), -(1 << 31) + 1, -65537, -1, 0, 1,
                (1 << 24) - 1, 1 << 24, (1 << 31) - 1],
        "u32": [0, 1, (1 << 24) + 1, (1 << 32) - 1, 1 << 31],
        "i64": [-(1 << 63), -(1 << 63) + 1, -(1 << 53) - 1, -1, 0, 1,
                (1 << 53) - 1, 1 << 53, (1 << 53) + 1, (1 << 63) - 1],
        "u64": [0, 1, (1 << 53) - 1, 1 << 53, (1 << 53) + 2,
                (1 << 64) - 1, 1 << 63],
    }
    for itok, vals in intvals.items():
        w = INT_RANGES[itok][2]
        for v in vals:
            for rm in RMS:
                r, f = ref_from_int(v, rm)
                out.append(line("msf64_from_" + itok, rm,
                                [v & ((1 << w) - 1)], r, f, prov))
    fr = Fraction
    fvals = [fr(0), fr(1, 2), -fr(1, 2), fr(3, 2), -fr(3, 2),
             fr(5, 2), fr(127), fr(255, 2), -fr(255, 2),
             fr(128), -fr(128), fr(255), fr(511, 2), fr(256),
             fr(32767), fr(65535, 2), fr(2) ** 31, -fr(2) ** 31,
             fr(2) ** 63, -fr(2) ** 63, fr(2) ** 64,
             fr(1, 1024), -fr(1, 1024), fr(1234567, 128),
             fr(2) ** 53, fr(2) ** 100]
    fbits = [make_bits("f64", v) for v in fvals]
    fbits += [0x8000000000000000, 0x7FF0000000000000,
              0xFFF0000000000000, 1,
              0x7FEFFFFFFFFFFFFF]
    fbits += nan_pool64()[:2]
    modes = [("ties_to_even", "te", 0), ("ties_to_away", "ta", 0),
             ("toward_zero", "tz", 0), ("toward_positive", "tp", 0),
             ("toward_negative", "tn", 0),
             ("exact_ties_to_even", "te", 1),
             ("exact_ties_to_away", "ta", 1),
             ("exact_toward_zero", "tz", 1),
             ("exact_toward_positive", "tp", 1),
             ("exact_toward_negative", "tn", 1)]
    for itok in intvals:
        for suf, mode, ex in modes:
            for a in fbits:
                r, f = ref_to_int(a, mode, ex, itok)
                out.append(line("msf64_to_%s_%s" % (itok, suf), "-",
                                [a], r, f, prov))
    return out


def directed_misc(prov):
    out = []
    fr = Fraction
    vals = [fr(0), fr(1, 2), -fr(1, 2), fr(3, 2), -fr(3, 2),
            fr(5, 2), -fr(5, 2), fr(7, 2), fr(1, 4), -fr(3, 4),
            fr(2) ** 52, fr(2) ** 51 + fr(1, 2), fr(2) ** 53,
            fr(12345, 8), -fr(12345, 8), fr(1, 2 ** 60),
            fr(2) ** -1073 * 3]
    bits_list = [make_bits("f64", v) for v in vals]
    bits_list += [0x8000000000000000, 1, 0x8000000000000001,
                  0x0010000000000000, 0x7FEFFFFFFFFFFFFF,
                  0x7FF0000000000000, 0xFFF0000000000000]
    bits_list += nan_pool64()[:3]
    for suf, mode in (("ties_to_even", "te"), ("ties_to_away", "ta"),
                      ("toward_zero", "tz"),
                      ("toward_positive", "tp"),
                      ("toward_negative", "tn")):
        for a in bits_list:
            r, f = ref_rint(a, mode, 0)
            out.append(line("msf64_round_to_integral_" + suf, "-",
                            [a], r, f, prov))
    for rm in RMS:
        for a in bits_list:
            r, f = ref_rint(a, rm, 1)
            out.append(line("msf64_round_to_integral_exact", rm,
                            [a], r, f, prov))
    for a in pool64() + nan_pool64()[:3]:
        for nm, up in (("msf64_next_up", True), ("msf64_next_down", False)):
            r, f = ref_next(a, up)
            out.append(line(nm, "-", [a], r, f, prov))
        r, f = ref_logb(a)
        out.append(line("msf64_log_b", "-", [a], r, f, prov))
    rem_pairs = [(fr(5), fr(3)), (fr(-5), fr(3)), (fr(5), fr(-3)),
                 (fr(7), fr(2)), (fr(9), fr(2)), (fr(1), fr(3)),
                 (fr(2) ** 100 + fr(2) ** 50, fr(7)),
                 (fr(2) ** -100, fr(2) ** 50),
                 (fr(2) ** 900, fr(2) ** -900 + fr(2) ** -950),
                 (fr(1234567, 64), fr(123, 16)),
                 (fr(3, 2), fr(1, 2)), (fr(5, 2), fr(1)),
                 (fr(0), fr(3)), (fr(2) ** -1074, fr(1)),
                 (fr(1), fr(2) ** -1074)]
    for xv, yv in rem_pairs:
        yv_bits = make_bits("f64", yv) if yv != fr(2) ** -900 + fr(2) ** -950 \
            else make_bits("f64", fr(2) ** -900)
        a, b = make_bits("f64", xv), yv_bits
        r, f = ref_remainder(a, b)
        out.append(line("msf64_remainder", "-", [a, b], r, f, prov))
    for a in pool64()[::4]:
        for b in pool64()[1::5]:
            r, f = ref_remainder(a, b)
            out.append(line("msf64_remainder", "-", [a, b], r, f, prov))
    nvals = [fr(0), -fr(1) * 0, fr(1), fr(-1), fr(13, 4), -fr(13, 4),
             fr(1023), fr(-1022), fr(2045), fr(-2045), fr(5000),
             fr(-6000), fr(1, 2), -fr(1, 2), fr(2) ** 60]
    nbits = [make_bits("f64", v) for v in nvals]
    nbits += [0x8000000000000000, 0x7FF0000000000000,
              0xFFF0000000000000, 1]
    nbits += nan_pool64()[:2]
    for a in pool64()[::7]:
        for nb in nbits:
            for rm in RMS:
                r, f = ref_scaleb(a, nb, rm)
                out.append(line("msf64_scale_b", rm, [a, nb], r, f, prov))
    return out


def directed_compare(prov):
    out = []
    pa = pool64()[::3] + nan_pool64()
    pb64 = pool64()[1::3] + nan_pool64()[::-1]
    pb32 = pool32()[::2] + nan_pool32()
    pairs64 = [(a, b) for a in pa for b in pb64[::2]]
    pairs32 = [(a, b) for a in pa for b in pb32[::2]]
    for suf, code, sig in PREDICATES:
        for a, b in pairs64[::12]:
            r, f = ref_compare("f64", a, "f64", b, code, sig)
            out.append(line("msf64_compare_" + suf, "-", [a, b],
                            r, f, prov))
        for a, b in pairs32[::12]:
            r, f = ref_compare("f64", a, "f32", b, code, sig)
            out.append(line("msf64_compare_%s_f32" % suf, "-",
                            [a, b], r, f, prov))
    tot = pool64() + nan_pool64()
    for a in tot:
        for b in tot[::6]:
            r, f = ref_total(a, b, False)
            out.append(line("msf64_total_order", "-", [a, b], r, f, prov))
            r, f = ref_total(a, b, True)
            out.append(line("msf64_total_order_mag", "-", [a, b],
                            r, f, prov))
    return out


def directed_nan(prov):
    out = []
    one64 = make_bits("f64", Fraction(1))
    one32 = make_bits("f32", Fraction(1))
    zero64, inf64 = 0, 0x7FF0000000000000
    for a in nan_pool64():
        for b in [one64, zero64, inf64, nan_pool64()[0]]:
            for nm, fn in (("msf64_add", lambda x, y, r: ref_addsub("f64", x, "f64", y, False, r)),
                           ("msf64_mul", lambda x, y, r: ref_mul("f64", x, "f64", y, r)),
                           ("msf64_div", lambda x, y, r: ref_div("f64", x, "f64", y, r))):
                r, f = fn(a, b, "te")
                out.append(line(nm, "te", [a, b], r, f, prov))
                r, f = fn(b, a, "te")
                out.append(line(nm, "te", [b, a], r, f, prov))
        r, f = ref_sqrt("f64", a, "te")
        out.append(line("msf64_sqrt", "te", [a], r, f, prov))
        r, f = ref_conv("f64", a, "te")
        out.append(line("msf64_from_f64", "te", [a], r, f, prov))
        r, f = ref_rint(a, "te", 0)
        out.append(line("msf64_round_to_integral_ties_to_even", "-",
                        [a], r, f, prov))
        r, f = ref_next(a, True)
        out.append(line("msf64_next_up", "-", [a], r, f, prov))
        r, f = ref_logb(a)
        out.append(line("msf64_log_b", "-", [a], r, f, prov))
        r, f = ref_remainder(a, one64)
        out.append(line("msf64_remainder", "-", [a, one64], r, f, prov))
        r, f = ref_scaleb(one64, a, "te")
        out.append(line("msf64_scale_b", "te", [one64, a], r, f, prov))
        r, f = ref_fma("f64", zero64, "f64", inf64, "f64", a, "te")
        out.append(line("msf64_fma", "te", [zero64, inf64, a], r, f, prov))
        r, f = ref_fma("f64", a, "f64", one64, "f64", one64, "te")
        out.append(line("msf64_fma", "te", [a, one64, one64], r, f, prov))
    for a in nan_pool32():
        r, f = ref_conv("f32", a, "te")
        out.append(line("msf64_from_f32", "te", [a], r, f, prov))
        r, f = ref_addsub("f32", a, "f32", one32, False, "te")
        out.append(line("msf64_add_f32_f32", "te", [a, one32], r, f, prov))
        r, f = ref_compare("f64", one64, "f32", a, "eq", 0)
        out.append(line("msf64_compare_quiet_equal_f32", "-",
                        [one64, a], r, f, prov))
    return out


def rand_bits(rng, fmt, special_pools):
    bits, p, w, t, emax, emin = fmt_params(fmt)
    roll = rng.random()
    if roll < 0.08:
        return rng.choice(special_pools[fmt])
    sign = rng.randrange(2) << (bits - 1)
    if roll < 0.18:
        return sign | rng.randrange(0, 1 << t)
    e = rng.choice([rng.randrange(1, 6), rng.randrange(1, (1 << w) - 1),
                    rng.randrange((1 << w) - 6, (1 << w) - 1),
                    (emax - 1) + rng.randrange(0, 3)])
    e = max(1, min((1 << w) - 2, e))
    frac = rng.getrandbits(t)
    if rng.random() < 0.15:
        frac &= (1 << rng.randrange(1, 10)) - 1
    return sign | (e << t) | frac


def sweep(n, seed, prov):
    rng = random.Random(seed)
    specials = {"f64": pool64() + nan_pool64(),
                "f32": pool32() + nan_pool32()}
    binops = []
    for base in ("add", "sub", "mul", "div"):
        for fa, fb in (("f32", "f32"), ("f32", "f64"), ("f64", "f32")):
            binops.append((base, fa, fb))
    out = []
    for i in range(n):
        kind = i % 20
        rm = rng.choice(RMS)
        if kind < 12:
            base, fa, fb = binops[rng.randrange(len(binops))]
            a = rand_bits(rng, fa, specials)
            b = rand_bits(rng, fb, specials)
            if base == "add":
                r, f = ref_addsub(fa, a, fb, b, False, rm)
            elif base == "sub":
                r, f = ref_addsub(fa, a, fb, b, True, rm)
            elif base == "mul":
                r, f = ref_mul(fa, a, fb, b, rm)
            else:
                r, f = ref_div(fa, a, fb, b, rm)
            out.append(line("msf64_%s_%s_%s" % (base, fa, fb), rm,
                            [a, b], r, f, prov))
        elif kind < 15:
            a = rand_bits(rng, "f32", specials)
            r, f = ref_sqrt("f32", a, rm)
            out.append(line("msf64_sqrt_f32", rm, [a], r, f, prov))
        elif kind < 19:
            fa, fb, fc = (rng.choice(("f32", "f64")) for _ in range(3))
            if (fa, fb, fc) == ("f64", "f64", "f64"):
                fc = "f32"
            a = rand_bits(rng, fa, specials)
            b = rand_bits(rng, fb, specials)
            c = rand_bits(rng, fc, specials)
            r, f = ref_fma(fa, a, fb, b, fc, c, rm)
            out.append(line("msf64_fma_%s_%s_%s" % (fa, fb, fc), rm,
                            [a, b, c], r, f, prov))
        else:
            a = rand_bits(rng, "f32", specials)
            r, f = ref_conv("f32", a, rm)
            out.append(line("msf64_from_f32", rm, [a], r, f, prov))
    return out


def main(argv):
    mode = argv[1]
    if mode == "directed":
        outdir = Path(argv[2])
        write(outdir / "arith-f64.vec",
              directed_arith("exact-f64:directed-arith"))
        write(outdir / "conv-f64.vec",
              directed_conv("exact-f64:directed-conv"))
        write(outdir / "misc-f64.vec",
              directed_misc("exact-f64:directed-misc"))
        write(outdir / "compare-f64.vec",
              directed_compare("exact-f64:directed-compare"))
        write(outdir / "nan-f64.vec", directed_nan("exact-f64:directed-nan"))
    elif mode == "sweep":
        n = int(argv[3])
        seed = int(argv[4], 0) if len(argv) > 4 else 0xF64
        write(Path(argv[2]), sweep(n, seed, "exact-f64:cross-sweep"))
        print("sweep seed %d cases %d" % (seed, n))
    else:
        raise SystemExit("unknown mode %s" % mode)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

