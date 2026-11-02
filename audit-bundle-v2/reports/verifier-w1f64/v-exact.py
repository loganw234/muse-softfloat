#!/usr/bin/env python3
"""verifier-w164 (3): OWN exact-rational reference probe for wave-1 msf64_.

Independent from-scratch Fraction reference (never imports the copy's
tests/gen_vectors_f64.py): decode, exact op value, single correct
rounding with tininess-after-rounding, Clause 6/7 specials, SF-0 2.5
NaN matrix, header saturation rule, scaleB truncation ruling.
Emits runner-format .vec files with provenance exact-w164:<family>.
"""
import random
import sys
from fractions import Fraction
from pathlib import Path

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("exact-tmp")
OUT.mkdir(parents=True, exist_ok=True)

P = 53
EMAX = 1023
EMIN = -1022
T = 52
F_INV, F_DIV0, F_OVF, F_UNF, F_INX = 0x01, 0x02, 0x04, 0x08, 0x10
RMS = ["te", "tz", "tp", "tn"]
QDEFAULT = 0x7FF8000000000000


def params():
    return P, EMAX, EMIN, T


def decode(x):
    sign = (x >> 63) & 1
    ef = (x >> T) & 0x7FF
    fr = x & ((1 << T) - 1)
    if ef == 0x7FF:
        cls = "inf" if fr == 0 else ("qnan" if (fr >> (T - 1)) & 1 else "snan")
        return {"sign": sign, "cls": cls, "frac": fr, "val": Fraction(0, 1)}
    if ef == 0:
        cls = "zero" if fr == 0 else "sub"
        sig = fr
        exp = EMIN - T
    else:
        cls = "norm"
        sig = fr | (1 << T)
        exp = ef - EMAX - T
    v = Fraction(sig << exp, 1) if exp >= 0 else Fraction(sig, 1 << (-exp))
    return {"sign": sign, "cls": cls, "frac": fr, "sig": sig, "exp": exp,
            "val": -v if sign else v}


def is_nan(d):
    return d["cls"] in ("qnan", "snan")


def widen_nan(src_bits):
    """f32 NaN bits -> f64 NaN bits (payload shift left, quiet kept)."""
    s = (src_bits >> 31) & 1
    ef = (src_bits >> 23) & 0xFF
    fr = src_bits & 0x7FFFFF
    assert ef == 0xFF and fr != 0
    q = 1 if (fr >> 22) & 1 else 0
    return (s << 63) | (0x7FF << T) | (q << (T - 1)) | (fr << (T - 23))


def nan_delivery(dest_fmt_bits, ops, extra_invalid):
    """ops: list of (bits, is_f32). Returns (bits, flags) or None.
    Signaling inputs take precedence over quiet ones (SF-0 2.5b)."""
    first_s = None
    first_q = None
    for b, is32 in ops:
        if is32:
            s = (b >> 31) & 1
            ef = (b >> 23) & 0xFF
            fr = b & 0x7FFFFF
            if ef != 0xFF or fr == 0:
                continue
            if ((fr >> 22) & 1) == 0:
                if first_s is None:
                    first_s = widen_nan(b | (1 << 22))
            else:
                if first_q is None:
                    first_q = widen_nan(b)
        else:
            d = decode(b)
            if not is_nan(d):
                continue
            if d["cls"] == "snan":
                if first_s is None:
                    first_s = b | (1 << (T - 1))
            else:
                if first_q is None:
                    first_q = b
    if first_s is not None:
        return first_s, F_INV
    if first_q is not None:
        return first_q, 0
    if extra_invalid:
        return QDEFAULT, F_INV
    return None


def pow2(e):
    return Fraction(1 << e, 1) if e >= 0 else Fraction(1, 1 << (-e))


def _round_bit(qi, frac, rm, sign, halve_ok_even=True):
    if rm == "te":
        if frac > Fraction(1, 2):
            return qi + 1
        if frac == Fraction(1, 2) and (qi & 1):
            return qi + 1
        return qi
    if rm == "tz":
        return qi
    if rm == "tp":
        return qi + (1 if (frac > 0 and sign == 0) else 0)
    if rm == "tn":
        return qi + (1 if (frac > 0 and sign == 1) else 0)
    raise ValueError(rm)


def _round_inc(rm, sign, cand, guard, rbit, stick):
    inex = guard or rbit or stick
    if rm == "te":
        return 1 if (guard and (rbit or stick or (cand & 1))) else 0
    if rm == "ta":
        return 1 if inex else 0
    if rm == "tp":
        return 1 if ((sign == 0) and inex) else 0
    if rm == "tn":
        return 1 if ((sign == 1) and inex) else 0
    return 0


def _window(num, den, K, sticky_in):
    """Exact (p+2)-bit window of num/den at scale K: value*2^K = Q2 + R/D.
    Returns (cand, guard, rbit, stick)."""
    if K >= 0:
        q, r = divmod(num << K, den)
    else:
        q, r = divmod(num, den << (-K))
    return q >> 2, (q >> 1) & 1, q & 1, (r != 0) or bool(sticky_in)


def pack_core(sign, num, den, sticky_in, rm):
    """Mirror of msf_pack_generic over exact integers: single rounding,
    Clause 7.5 unbounded tininess-after-rounding for underflow."""
    if num == 0:
        if not sticky_in:
            return (sign << 63), 0
        up = (rm == "tp" and sign == 0) or (rm == "tn" and sign == 1)
        return ((sign << 63) | (1 if up else 0)), (F_UNF | F_INX)
    d = num.bit_length() - den.bit_length()
    if d >= 0:
        e = d if num >= (den << d) else d - 1
    else:
        e = d if ((num << (-d)) >= den) else d - 1
    e_bits = e
    ec = e if e >= EMIN else EMIN
    # main window at clamped scale: value*2^K has top near bit P+1
    cand, guard, rbit, stick = _window(num, den, (P + 1) - ec, sticky_in)
    inex = guard or rbit or stick
    cand += _round_inc(rm, sign, cand, guard, rbit, stick)
    ec2 = ec
    if (cand >> P) != 0:
        cand >>= 1
        ec2 += 1
    if ec2 > EMAX:
        to_inf = rm == "te" or (rm == "tp" and sign == 0) \
            or (rm == "tn" and sign == 1)
        enc = (0x7FF << T) if to_inf else ((0x7FE << T) | ((1 << T) - 1))
        return ((sign << 63) | enc), F_OVF | F_INX
    fl = 0
    if inex:
        tiny_before = e_bits < EMIN
        tiny_after = 0
        if tiny_before:
            Ku = (P + 1) - e_bits
            cu, gu, ru, su = _window(num, den, Ku, sticky_in)
            cu += _round_inc(rm, sign, cu, gu, ru, su)
            er = e_bits + (1 if (cu >> P) != 0 else 0)
            tiny_after = er < EMIN
        fl = F_INX | (F_UNF if tiny_after else 0)
    if cand >= (1 << (P - 1)):
        return ((sign << 63) | ((ec2 + EMAX) << T)
                | (cand - (1 << (P - 1)))), fl
    return ((sign << 63) | cand), fl


def pack_value(v, rm):
    s = 1 if v < 0 else 0
    m = -v if s else v
    return pack_core(s, m.numerator, m.denominator, False, rm)


def pack_signed_zero(s, rm):
    return pack_core(s, 0, 1, False, rm)


def pack_frac(value, sign, rm):
    """Compat shim over pack_core (unbounded Clause 7.5 tininess)."""
    if value == 0:
        return pack_signed_zero(sign, rm)
    return pack_value(value, rm)


def zero_sum_sign(s1, s2, rm):
    return s1 if s1 == s2 else (1 if rm == "tn" else 0)


def dec(b, is32):
    return decode_f32(b) if is32 else decode(b)


def ref_addsub(a, b, is32a, is32b, is_sub, rm):
    da = dec(a, is32a)
    db = dec(b, is32b)
    es = db["sign"] ^ (1 if is_sub else 0)
    inv = da["cls"] == "inf" and db["cls"] == "inf" and da["sign"] != es
    nd = nan_delivery(0, [(a, is32a), (b, is32b)], inv)
    if nd:
        return nd
    if da["cls"] == "inf":
        return (da["sign"] << 63) | (0x7FF << T), 0
    if db["cls"] == "inf":
        return (es << 63) | (0x7FF << T), 0
    va, vb = da["val"], db["val"]
    if is_sub:
        vb = -vb
    v = va + vb
    if v == 0:
        if va == 0 and vb == 0:
            s = zero_sum_sign(da["sign"], es, rm)
        else:
            s = 1 if rm == "tn" else 0
        return pack_frac(Fraction(0, 1), s, rm)
    return pack_frac(v, 0 if v > 0 else 1, rm)


def ref_mul(a, b, is32a, is32b, rm):
    da = dec(a, is32a)
    db = dec(b, is32b)
    sign = da["sign"] ^ db["sign"]
    inv = (da["cls"] == "zero" and db["cls"] == "inf") \
        or (da["cls"] == "inf" and db["cls"] == "zero")
    nd = nan_delivery(0, [(a, is32a), (b, is32b)], inv)
    if nd:
        return nd
    if da["cls"] == "inf" or db["cls"] == "inf":
        return (sign << 63) | (0x7FF << T), 0
    if da["cls"] == "zero" or db["cls"] == "zero":
        return (sign << 63), 0
    v = da["val"] * db["val"]
    return pack_frac(v, 0 if v > 0 else 1, rm)


def ref_div(a, b, is32a, is32b, rm):
    da = dec(a, is32a)
    db = dec(b, is32b)
    sign = da["sign"] ^ db["sign"]
    inv = (da["cls"] == "zero" and db["cls"] == "zero") \
        or (da["cls"] == "inf" and db["cls"] == "inf")
    nd = nan_delivery(0, [(a, is32a), (b, is32b)], inv)
    if nd:
        return nd
    if da["cls"] == "inf":
        return (sign << 63) | (0x7FF << T), 0
    if db["cls"] == "inf" or da["cls"] == "zero":
        return (sign << 63), 0
    if db["cls"] == "zero":
        return ((sign << 63) | (0x7FF << T)), F_DIV0
    v = da["val"] / db["val"]
    return pack_frac(v, 0 if v > 0 else 1, rm)


def ref_sqrt(a, rm, is32=False):
    from math import isqrt as _isqrt
    da = dec(a, is32)
    inv = bool(da["sign"]) and da["cls"] != "zero"
    nd = nan_delivery(0, [(a, is32)], inv)
    if nd:
        return nd
    if da["cls"] == "inf":
        return (0x7FF << T), 0
    if da["cls"] == "zero":
        return (da["sign"] << 63), 0
    num, den = da["val"].numerator, da["val"].denominator
    K = 1 << 1200
    # t = floor(sqrt(num/den)*K); sticky exact via integers:
    # sqrt(num/den)*K = t  <=>  num*K^2 = t^2*den
    t = _isqrt((num * K * K) // den)
    sticky = (num * K * K - t * t * den) != 0
    # value = t/K with sticky below the quantum: pack through pack_core
    return pack_core(0, t, K, sticky, rm)


def ref_fma(x, y, c, s32x, s32y, s32c, rm):
    dx, dy, dc = dec(x, s32x), dec(y, s32y), dec(c, s32c)
    ps = dx["sign"] ^ dy["sign"]
    prod_inv = (dx["cls"] == "zero" and dy["cls"] == "inf") \
        or (dx["cls"] == "inf" and dy["cls"] == "zero")
    prod_inf = (dx["cls"] == "inf" or dy["cls"] == "inf") \
        and dx["cls"] != "zero" and dy["cls"] != "zero" \
        and not is_nan(dx) and not is_nan(dy)
    # project ruling: 0*inf + quiet-NaN addend -> invalid, deliver addend
    ruling = prod_inv and dc["cls"] == "qnan"
    inv = prod_inv or (prod_inf and dc["cls"] == "inf" and dc["sign"] != ps)
    nd = nan_delivery(0, [(x, s32x), (y, s32y), (c, s32c)], inv and not ruling)
    if ruling:
        qb = widen_nan(c) if s32c else c
        return qb, F_INV
    if nd:
        return nd
    if prod_inf:
        return (ps << 63) | (0x7FF << T), 0
    if dc["cls"] == "inf":
        return (dc["sign"] << 63) | (0x7FF << T), 0
    px = dx["val"] if dx["cls"] not in ("zero",) else Fraction(0, 1)
    py = dy["val"] if dy["cls"] not in ("zero",) else Fraction(0, 1)
    if dx["cls"] == "zero" or dy["cls"] == "zero":
        pv = Fraction(0, 1)
    else:
        pv = px * py
    cv = dc["val"] if dc["cls"] != "zero" else Fraction(0, 1)
    v = pv + cv
    if v == 0:
        if pv == 0 and cv == 0:
            s = zero_sum_sign(ps, dc["sign"], rm)
        else:
            s = 1 if rm == "tn" else 0
        return pack_frac(Fraction(0, 1), s, rm)
    return pack_frac(v, 0 if v > 0 else 1, rm)


def ref_rem(x, y):
    dx, dy = decode(x), decode(y)
    nd = nan_delivery(0, [(x, False), (y, False)],
                      (dx["cls"] == "inf") or (dy["cls"] == "zero"))
    if nd:
        return nd
    if dy["cls"] == "inf" or (dx["cls"] == "zero" and dy["cls"] != "zero"):
        return x if not (dx["cls"] == "zero") else ((dx["sign"] << 63)), 0
    if dx["cls"] == "zero":
        return (dx["sign"] << 63), 0
    # finite nonzero: n = ties-even integer nearest x/y; r = x - n*y
    q = dx["val"] / dy["val"]
    fl = q.numerator // q.denominator
    rem = q - fl
    if rem > Fraction(1, 2) or (rem == Fraction(1, 2) and (fl & 1)):
        n = fl + 1
    elif rem < 0 and False:
        n = fl
    else:
        n = fl
    if q < 0:
        fl2 = (-q).numerator // (-q).denominator
        rem2 = (-q) - fl2
        if rem2 > Fraction(1, 2) or (rem2 == Fraction(1, 2) and (fl2 & 1)):
            n = -(fl2 + 1)
        else:
            n = -fl2
    r = dx["val"] - n * dy["val"]
    if r == 0:
        return (dx["sign"] << 63), 0
    # exact result: encode directly
    return pack_frac(r, 0 if r > 0 else 1, "te")


def _round_int_frac(v, mode):
    mode = {"ties_to_even": "te", "ties_to_away": "ta",
            "toward_zero": "tz", "toward_positive": "tp",
            "toward_negative": "tn"}.get(mode, mode)
    fl = v.numerator // v.denominator
    rem = v - fl
    if mode in ("tz",):
        return fl if v >= 0 or rem == 0 else fl + 1
    if mode in ("tp",):
        return fl + (1 if rem else 0)
    if mode in ("tn",):
        return fl
    if mode in ("ta",):
        if v < 0:
            return -_round_int_frac(-v, "ta")
        return fl + (1 if rem >= Fraction(1, 2) else 0)
    if rem > Fraction(1, 2) or (rem == Fraction(1, 2) and (fl & 1)):
        return fl + 1
    return fl


def ref_rint(a, mode, exact_form, dyn_rm):
    da = decode(a)
    nd = nan_delivery(0, [(a, False)], False)
    if nd:
        return nd
    if da["cls"] in ("inf", "zero"):
        return a, 0
    v = da["val"]
    m = _round_int_frac(v, mode if not exact_form else
                        {"te": "te", "tz": "tz", "tp": "tp", "tn": "tn"}[dyn_rm])
    fl = 0
    if exact_form and Fraction(m, 1) != v:
        fl = F_INX
    s = da["sign"] if m == 0 else (0 if m > 0 else 1)
    return pack_frac(Fraction(m, 1), s, "te")[0], fl


def ref_to_int(a, width, signed, mode, exact_form):
    da = decode(a)
    mask = (1 << width) - 1
    if is_nan(da):
        return 0, F_INV
    if da["cls"] == "inf":
        if signed:
            lo_i, hi_i = -(1 << (width - 1)), (1 << (width - 1)) - 1
            return ((lo_i if da["sign"] else hi_i) & mask), F_INV
        return (mask if da["sign"] == 0 else 0), F_INV
    v = da["val"]
    m = _round_int_frac(v, mode)
    inx = (Fraction(m, 1) != v)
    if signed:
        lo, hi = -(1 << (width - 1)), (1 << (width - 1)) - 1
    else:
        lo, hi = 0, (1 << width) - 1
    if m < lo:
        return ((lo & mask)), F_INV
    if m > hi:
        return ((hi & mask)), F_INV
    return (m & mask), (F_INX if (exact_form and inx) else 0)


def ref_from_int(n, width, signed, rm="te"):
    if signed and n >= (1 << (width - 1)):
        n -= 1 << width
    if not signed:
        n &= (1 << width) - 1
    return pack_frac(Fraction(n, 1), 0 if n >= 0 else 1, rm)


def ref_compare(pred, a, b, is32b):
    da = decode(a)
    dbb = decode(b) if not is32b else None
    if is32b:
        s = (b >> 31) & 1
        ef = (b >> 23) & 0xFF
        fr = b & 0x7FFFFF
        if ef == 0xFF:
            db = {"sign": s, "cls": "inf" if fr == 0 else
                  ("qnan" if (fr >> 22) & 1 else "snan"),
                  "val": Fraction(0, 1)}
        elif ef == 0:
            db = {"sign": s, "cls": "zero" if fr == 0 else "sub",
                  "val": Fraction(fr, 1 << 149) * (-1 if s else 1)}
        else:
            sh = (ef - 127) - 23
            vv = Fraction((fr | (1 << 23)) << sh, 1) if sh >= 0 \
                else Fraction(fr | (1 << 23), 1 << (-sh))
            db = {"sign": s, "cls": "norm", "val": vv * (-1 if s else 1)}
    else:
        db = dbb
    an, bn = is_nan(da), is_nan(db)
    asnan = da["cls"] == "snan"
    bsns = db["cls"] == "snan"
    signaling = pred.startswith("signaling")
    fl = F_INV if (an or bn) and (signaling or asnan or bsns) else 0
    # relation on finite/non-nan
    if an or bn:
        lt = eq = False
    else:
        va = da["val"]
        vb = db["val"]
        if da["cls"] == "inf":
            va = Fraction(10**400, 1) if da["sign"] == 0 else Fraction(-10**400, 1)
        if db["cls"] == "inf":
            vb = Fraction(10**400, 1) if db["sign"] == 0 else Fraction(-10**400, 1)
        lt = va < vb
        eq = va == vb
    un = an or bn
    base = pred.split("_", 1)[1]
    if base == "equal":
        r = eq and not un
    elif base == "not_equal":
        r = (not eq) or un
    elif base == "less":
        r = lt
    elif base == "less_equal":
        r = lt or (eq and not un)
    elif base == "greater":
        r = (not lt) and (not eq) and (not un)
    elif base == "greater_equal":
        r = (not lt) and (not un)
    elif base == "not_less":
        r = (not lt)
    elif base == "not_greater":
        r = lt or eq or un
    elif base == "less_unordered":
        r = lt or un
    elif base == "greater_unordered":
        r = ((not lt) and (not eq)) or un
    elif base == "unordered":
        r = un
    elif base == "ordered":
        r = not un
    else:
        raise ValueError(pred)
    return (1 if r else 0), fl


def ref_next(a, up):
    da = decode(a)
    nd = nan_delivery(0, [(a, False)], False)
    if nd:
        b, f = nd
        return b, (f | 0)
    if da["cls"] == "inf":
        if (da["sign"] == 0) == up:
            return a, 0
        return (da["sign"] << 63) | (0x7FE << T) | ((1 << T) - 1), 0
    if da["cls"] == "zero":
        return ((0 if up else 1) << 63) | 1, 0
    mag_up = (da["sign"] == 0) == up
    return ((a + 1) & ((1 << 64) - 1)) if mag_up else (a - 1), 0


def ref_scaleb(x, nbits, rm):
    dx, dn = decode(x), decode(nbits)
    nd = nan_delivery(0, [(x, False), (nbits, False)], False)
    if nd:
        return nd
    if dx["cls"] in ("zero", "inf"):
        return x, 0
    if dn["cls"] == "inf":
        big = 5000 if dn["sign"] == 0 else -5000
        return pack_frac(dx["val"] * pow2(big) if big > 0
                         else dx["val"] / pow2(-big),
                         dx["sign"], rm)
    if dn["cls"] == "zero":
        return pack_frac(dx["val"], dx["sign"], rm)
    nv = dn["val"]
    nint = int(nv)  # truncates toward zero
    if abs(nint) > 5000:
        nint = 5000 if nint > 0 else -5000
    v = dx["val"] * pow2(nint) if nint >= 0 \
        else dx["val"] / pow2(-nint)
    return pack_frac(v, dx["sign"], rm)


def ref_logb(a):
    da = decode(a)
    nd = nan_delivery(0, [(a, False)], False)
    if nd:
        return nd
    if da["cls"] == "zero":
        return (1 << 63) | (0x7FF << T), F_DIV0
    if da["cls"] == "inf":
        return (0x7FF << T), 0
    e = da["exp"] + da["sig"].bit_length() - 1
    return pack_frac(Fraction(e, 1), 0 if e >= 0 else 1, "te")


def order_key(bits, mag):
    d = decode(bits)
    s = 0 if mag else d["sign"]
    if d["cls"] == "qnan":
        return (11 if s == 0 else 0, 0, d["frac"])
    if d["cls"] == "snan":
        return (10 if s == 0 else 1, 0, d["frac"])
    if d["cls"] == "inf":
        return (9 if s == 0 else 2, 0, 0)
    if d["cls"] == "zero":
        return (6 if s == 0 else 5, 0, 0)
    v = d["val"] if d["cls"] != "zero" else Fraction(0, 1)
    av = -v if v < 0 else v
    if s == 0:
        return (8 if d["cls"] == "norm" else 7, av, 0)
    return (3 if d["cls"] == "norm" else 4, av, 0)


def ref_total_order(a, b, mag):
    ka, kb = order_key(a, mag), order_key(b, mag)
    # negative-number magnitudes order reversed: more-negative is less
    def adj(k):
        rank, magv, pay = k
        if rank in (3, 4):
            return (rank, _Neg(magv), pay)
        return (rank, _Pos(magv), pay)
    return (1 if adj(ka) <= adj(kb) else 0), 0


class _Neg:
    def __init__(self, v):
        self.v = v
    def __lt__(self, o):
        return self.v > o.v
    def __eq__(self, o):
        return self.v == o.v
    def __le__(self, o):
        return self.v >= o.v


class _Pos:
    def __init__(self, v):
        self.v = v
    def __lt__(self, o):
        return self.v < o.v
    def __eq__(self, o):
        return self.v == o.v
    def __le__(self, o):
        return self.v <= o.v


def f32bits(sign, ef, fr):
    return (sign << 31) | (ef << 23) | fr


def decode_f32(b):
    s = (b >> 31) & 1
    ef = (b >> 23) & 0xFF
    fr = b & 0x7FFFFF
    if ef == 0xFF:
        cls = "inf" if fr == 0 else ("qnan" if (fr >> 22) & 1 else "snan")
        return {"sign": s, "cls": cls, "frac": fr, "val": Fraction(0, 1)}
    if ef == 0:
        cls = "zero" if fr == 0 else "sub"
        sig, exp = fr, -126 - 23
    else:
        cls = "norm"
        sig, exp = fr | (1 << 23), ef - 127 - 23
    v = Fraction(sig << exp, 1) if exp >= 0 else Fraction(sig, 1 << (-exp))
    return {"sign": s, "cls": cls, "frac": fr, "sig": sig, "exp": exp,
            "val": -v if s else v}


def ref_from_f32(b, rm):
    d = decode_f32(b)
    nd = nan_delivery(0, [(b, True)], False)
    if nd:
        return nd
    if d["cls"] == "inf":
        return (d["sign"] << 63) | (0x7FF << T), 0
    if d["cls"] == "zero":
        return (d["sign"] << 63), 0
    return pack_frac(d["val"], d["sign"], rm)


def ref_from_f64(b, rm):
    nd = nan_delivery(0, [(b, False)], False)
    if nd:
        return nd
    return b, 0


# ---------------- case pools (directed encodings of my choice) ----------------
PZERO, NZERO = 0x0, 0x8000000000000000
PINF, NINF = 0x7FF0000000000000, 0xFFF0000000000000
PMAX, NMAX = 0x7FEFFFFFFFFFFFFF, 0xFFEFFFFFFFFFFFFF
PMIN_N, NMIN_N = 0x0010000000000000, 0x8010000000000000
PMAX_S, NMAX_S = 0x000FFFFFFFFFFFFF, 0x800FFFFFFFFFFFFF
PMIN_S, NMIN_S = 0x1, 0x8000000000000001
PONE, NONE = 0x3FF0000000000000, 0xBFF0000000000000
PTWO, PHALF = 0x4000000000000000, 0x3FE0000000000000
P1P5, N1P5 = 0x3FF8000000000000, 0xBFF8000000000000
PTHREE, PFIVE = 0x4008000000000000, 0x4014000000000000
QNAN, QNAN_N = 0x7FF8000000000000, 0xFFF8000000000000
QNAN_P1 = 0x7FF8000000000001
QNAN_BIG = 0x7FFC000000000000
QNAN_MAX = 0x7FFFFFFFFFFFFFFF
SNAN, SNAN_N = 0x7FF0000000000001, 0xFFF0000000000001
SNAN_P = 0x7FF4000000000000

F_SPECIALS = [0x0, 0x80000000, 0x3F800000, 0xBF800000, 0x40000000,
              0x40400000, 0x7F800000, 0xFF800000, 0x7F7FFFFF, 0xFF7FFFFF,
              0x00800000, 0x80800000, 0x007FFFFF, 0x807FFFFF,
              0x00000001, 0x80000001, 0x7FC00000, 0xFFC00000,
              0x7FC00001, 0x7F800001, 0xFF800001, 0x7FA00000]

D_SPECIALS = [PZERO, NZERO, PINF, NINF, PMAX, NMAX, PMIN_N, NMIN_N,
              PMAX_S, NMAX_S, PMIN_S, NMIN_S, PONE, NONE, PTWO, PHALF,
              P1P5, N1P5, PTHREE, PFIVE, QNAN, QNAN_N, QNAN_P1, QNAN_BIG,
              QNAN_MAX, SNAN, SNAN_N, SNAN_P]

INT_WIDTHS = [(8, True), (8, False), (16, True), (16, False),
              (32, True), (32, False), (64, True), (64, False)]
INT_MODES = ["ties_to_even", "ties_to_away", "toward_zero",
             "toward_positive", "toward_negative"]
PREDS = ["quiet_equal", "quiet_not_equal", "signaling_equal",
         "signaling_not_equal", "quiet_greater", "quiet_greater_equal",
         "quiet_less", "quiet_less_equal", "quiet_not_greater",
         "quiet_not_less", "quiet_less_unordered",
         "quiet_greater_unordered", "quiet_unordered", "quiet_ordered",
         "signaling_greater", "signaling_greater_equal", "signaling_less",
         "signaling_less_equal", "signaling_not_greater",
         "signaling_not_less", "signaling_less_unordered",
         "signaling_greater_unordered"]


def hx(v, w=None):
    if v < 0:
        v &= (1 << (w or 64)) - 1
    s = "%x" % v
    return s


def emit(fh, op, rm, operands, result, flags, fam):
    if isinstance(result, int):
        r = hx(result)
    else:
        r = result
    fl = "--" if flags is None else ("%02x" % flags)
    fh.write("%s %s %s -> %s %s exact-w164:%s\n" %
             (op, rm, " ".join(operands), r, fl, fam))


def rnorm64(rng):
    s = rng.getrandbits(1)
    ef = rng.randint(1, 2046)
    fr = rng.getrandbits(52)
    return (s << 63) | (ef << T) | fr


def rsub64(rng):
    s = rng.getrandbits(1)
    fr = rng.getrandbits(52) | 1
    return (s << 63) | fr


def rnorm32(rng):
    s = rng.getrandbits(1)
    ef = rng.randint(1, 254)
    fr = rng.getrandbits(23)
    return (s << 31) | (ef << 23) | fr


def rsub32(rng):
    s = rng.getrandbits(1)
    return (s << 31) | (rng.getrandbits(23) | 1)


def main():
    rng = random.Random(0x164)
    counts = {}

    def fh(name):
        p = OUT / name
        f = open(p, "w", newline="\n")
        f.write("# verifier-w164 exact-rational probe - generated, do not edit\n")
        counts[name] = 0
        return f

    def put(f, name, op, rm, ops, res, fl, fam):
        emit(f, op, rm, ops, res, fl, fam)
        counts[name] += 1

    binops = [("add", False), ("sub", True), ("mul", None), ("div", None)]
    combos = [("", False, False), ("_f32_f32", True, True),
              ("_f32_f64", True, False), ("_f64_f32", False, True)]
    directs = [PZERO, NZERO, PINF, NINF, PMAX, NMAX, PMIN_N, PMIN_S,
               PONE, NONE, PTWO, PHALF, P1P5, QNAN, SNAN, SNAN_N,
               QNAN_P1, 0x3FF0000000000001, 0xBFF0000000000001,
               0x7FEFFFFFFFFFFFFF, 0x0010000000000001, 0x0000000000000002]
    f32dir = [0x0, 0x80000000, 0x3F800000, 0xBF800000, 0x40000000,
              0x7F800000, 0xFF800000, 0x7F7FFFFF, 0x00800000, 0x007FFFFF,
              0x00000001, 0x7FC00000, 0xFFC00000, 0x7F800001, 0xFF800001,
              0x7FC00001, 0x3F800001, 0xBF800001]
    f = fh("w164-arith.vec")
    for oname, is_sub in binops:
        for suf, s32a, s32b in combos:
            pool_a = f32dir if s32a else directs
            pool_b = f32dir if s32b else directs
            for rm in RMS:
                for a in pool_a:
                    for b in pool_b[::3]:
                        aa = a if not s32a else a
                        if oname == "add":
                            r, fl = ref_addsub(aa, b, s32a, s32b, False, rm)
                        elif oname == "sub":
                            r, fl = ref_addsub(aa, b, s32a, s32b, True, rm)
                        elif oname == "mul":
                            r, fl = ref_mul(aa, b, s32a, s32b, rm)
                        else:
                            r, fl = ref_div(aa, b, s32a, s32b, rm)
                        put(f, "w164-arith.vec", "msf64_" + oname + suf, rm,
                            [hx(aa), hx(b)], r, fl, "arith")
                for _ in range(60):
                    rgen = rng.random()
                    if s32a:
                        a = rnorm32(rng) if rgen < 0.9 else rsub32(rng)
                    else:
                        a = rnorm64(rng) if rgen < 0.9 else rsub64(rng)
                    rgen = rng.random()
                    if s32b:
                        b = rnorm32(rng) if rgen < 0.9 else rsub32(rng)
                    else:
                        b = rnorm64(rng) if rgen < 0.9 else rsub64(rng)
                    if oname == "add":
                        r, fl = ref_addsub(a, b, s32a, s32b, False, rm)
                    elif oname == "sub":
                        r, fl = ref_addsub(a, b, s32a, s32b, True, rm)
                    elif oname == "mul":
                        r, fl = ref_mul(a, b, s32a, s32b, rm)
                    else:
                        r, fl = ref_div(a, b, s32a, s32b, rm)
                    put(f, "w164-arith.vec", "msf64_" + oname + suf, rm,
                        [hx(a), hx(b)], r, fl, "arith")
    # div-by-zero directed (Clause 7.3) incl subnormal numerators
    for suf, s32a, s32b in combos:
        nums = [PONE, NONE, PMIN_S, NMIN_S, PMAX_S, PMAX, PMIN_N,
                0x3FF0000000000001] if not s32a else \
               [0x3F800000, 0xBF800000, 0x00000001, 0x007FFFFF, 0x7F7FFFFF]
        zeros = [0x0, 0x80000000] if s32b else [PZERO, NZERO]
        for rm in RMS:
            for a in nums:
                for b in zeros:
                    r, fl = ref_div(a, b, s32a, s32b, rm)
                    put(f, "w164-arith.vec", "msf64_div" + suf, rm,
                        [hx(a), hx(b)], r, fl, "div0")
    # zero-sum directed (Clause 6.3) in every mode
    for oname, is_sub in [("add", False), ("sub", True)]:
        for suf, s32a, s32b in combos:
            xs = [PONE, PMIN_S, PMAX, PMAX_S, PMIN_N] if not s32a else \
                [0x3F800000, 0x00000001, 0x7F7FFFFF, 0x007FFFFF, 0x00800000]
            for rm in RMS:
                for x in xs:
                    neg = x ^ (0x80000000 if s32a else 0x8000000000000000)
                    if not is_sub:
                        r, fl = ref_addsub(x, neg, s32a, s32b, False, rm)
                        put(f, "w164-arith.vec", "msf64_" + oname + suf, rm,
                            [hx(x), hx(neg)], r, fl, "zerosum")
                    else:
                        r, fl = ref_addsub(x, x, s32a, s32b, True, rm)
                        put(f, "w164-arith.vec", "msf64_" + oname + suf, rm,
                            [hx(x), hx(x)], r, fl, "zerosum")
    f.close()

    # fma: 8 combos, inf rules + ruling + zero sums + randoms
    f = fh("w164-fma.vec")
    fma_combos = [("", False, False, False), ("_f32_f32_f32", True, True, True),
                  ("_f32_f32_f64", True, True, False),
                  ("_f32_f64_f32", True, False, True),
                  ("_f32_f64_f64", True, False, False),
                  ("_f64_f32_f32", False, True, True),
                  ("_f64_f32_f64", False, True, False),
                  ("_f64_f64_f32", False, False, True)]
    inf_cases = [(PINF, PTWO, PINF), (PINF, PTWO, NINF), (NINF, PTWO, PINF),
                 (PZERO, PINF, QNAN), (PZERO, PINF, QNAN_N),
                 (PZERO, PINF, PONE), (PZERO, NINF, SNAN),
                 (PINF, PZERO, QNAN_P1), (PONE, PTWO, PINF),
                 (PONE, PTWO, NINF), (PZERO, PZERO, NZERO),
                 (PZERO, PZERO, PZERO), (PMAX, PTWO, NMAX)]
    for fc in fma_combos:
        suf, fa, fb, fcc = fc
        for rm in RMS:
            for (x, y, c) in inf_cases:
                xx = x if not fa else 0x3F800000 if x == PONE else (
                    0x7F800000 if x in (PINF,) else (
                        0xFF800000 if x == NINF else (
                            0x0 if x == PZERO else 0x7FC00000)))
                yy = y if not fb else 0x40000000 if y == PTWO else (
                    0x7F800000 if y == PINF else (
                        0xFF800000 if y == NINF else 0x0))
                cc = c if not fcc else 0x7F800000 if c == PINF else (
                    0xFF800000 if c == NINF else (
                        0x3F800000 if c == PONE else (
                            0x80000000 if c == NZERO else (
                                0x0 if c == PZERO else 0x7FC00000))))
                r, fl = ref_fma(xx, yy, cc, fa, fb, fcc, rm)
                put(f, "w164-fma.vec", "msf64_fma" + suf, rm,
                    [hx(xx), hx(yy), hx(cc)], r, fl, "fma-special")
            for _ in range(30):
                xs = rnorm32(rng) if fa else rnorm64(rng)
                ys = rnorm32(rng) if fb else rnorm64(rng)
                cs = rnorm32(rng) if fcc else rnorm64(rng)
                r, fl = ref_fma(xs, ys, cs, fa, fb, fcc, rm)
                put(f, "w164-fma.vec", "msf64_fma" + suf, rm,
                    [hx(xs), hx(ys), hx(cs)], r, fl, "fma-rand")
    f.close()

    # sqrt incl negative/inf/zero matrix + randoms
    f = fh("w164-sqrt.vec")
    sq_pool = [PZERO, NZERO, PINF, NINF, PMAX, PMIN_N, PMIN_S, PMAX_S,
               PONE, PTWO, PHALF, 0x3FF0000000000001, QNAN, SNAN, SNAN_N,
               NONE, N1P5, 0x3FEFFFFFFFFFFFFF, 0x0010000000000001]
    for suf, s32 in [("", False), ("_f32", True)]:
        pool = f32dir if s32 else sq_pool
        for rm in RMS:
            for a in pool:
                r, fl = ref_sqrt(a, rm, s32)
                put(f, "w164-sqrt.vec", "msf64_sqrt" + suf, rm,
                    [hx(a)], r, fl, "sqrt")
            for _ in range(60):
                a = (rnorm32(rng) if rng.random() < 0.9 else rsub32(rng)) \
                    if s32 else \
                    (rnorm64(rng) if rng.random() < 0.9 else rsub64(rng))
                r, fl = ref_sqrt(a, rm, s32)
                put(f, "w164-sqrt.vec", "msf64_sqrt" + suf, rm,
                    [hx(a)], r, fl, "sqrt-rand")
    f.close()

    # compares: 22 preds x homogeneous/cross, NaN matrix + numbers
    f = fh("w164-compare.vec")
    num_pairs = [(PZERO, NZERO), (PZERO, PZERO), (PONE, PONE), (PONE, NONE),
                 (PONE, PTWO), (PMAX, PINF), (NINF, PINF), (PMIN_S, PZERO),
                 (NMIN_S, PZERO), (PMAX_S, PMIN_S), (PTHREE, PFIVE),
                 (0x3FF0000000000001, PONE), (PONE, 0x3FF0000000000001)]
    nan_vals = [QNAN, QNAN_N, QNAN_P1, QNAN_MAX, SNAN, SNAN_N, SNAN_P]
    nan_pairs = []
    for q in nan_vals:
        for w in [PONE, PZERO, NZERO, PINF, NINF, SNAN, QNAN_N, QNAN_P1]:
            nan_pairs.append((q, w))
            nan_pairs.append((w, q))
    for pred in PREDS:
        for suf, s32 in [("", False), ("_f32", True)]:
            for (a, b) in num_pairs:
                bb = b if not s32 else 0x3F800000 if b == PONE else (
                    0xBF800000 if b == NONE else (
                        0x40000000 if b == PTWO else (
                            0x7F800000 if b == PINF else (
                                0xFF800000 if b == NINF else (
                                    0x0 if b == PZERO else (
                                        0x80000000 if b == NZERO else
                                        0x40400000))))))
                r, fl = ref_compare(pred, a, bb, s32)
                put(f, "w164-compare.vec",
                    "msf64_compare_" + pred + suf, "-",
                    [hx(a), hx(bb)], r, fl, "cmp-num")
            for (a, b) in nan_pairs:
                bb = b if not s32 else 0x7FC00000 if b in (
                    QNAN, QNAN_N, QNAN_P1) else (
                    0x7F800001 if b in (SNAN, SNAN_N, SNAN_P) else (
                        0x3F800000 if b == PONE else (
                            0x0 if b == PZERO else (
                                0x80000000 if b == NZERO else (
                                    0x7F800000 if b == PINF else 0xFF800000)))))
                r, fl = ref_compare(pred, a, bb, s32)
                put(f, "w164-compare.vec",
                    "msf64_compare_" + pred + suf, "-",
                    [hx(a), hx(bb)], r, fl, "cmp-nan")
    f.close()

    # totalOrder/Mag over a compact pool (payload pairs included)
    f = fh("w164-total.vec")
    tpool = [PZERO, NZERO, PONE, NONE, PTWO, PMIN_S, NMIN_S, PMAX_S,
             PMAX, NMAX, PMIN_N, PINF, NINF, QNAN, QNAN_N, QNAN_P1,
             QNAN_BIG, SNAN, SNAN_N, SNAN_P, P1P5, 0x0000000000000002,
             0x7FEFFFFFFFFFFFFF, 0x0010000000000001]
    for mag, op in [(False, "msf64_total_order"),
                    (True, "msf64_total_order_mag")]:
        for a in tpool:
            for b in tpool:
                r, fl = ref_total_order(a, b, mag)
                put(f, "w164-total.vec", op, "-", [hx(a), hx(b)], r,
                    None, "total")
    f.close()

    # remainder: Clause 5.3.1 incl ties, signs, specials
    f = fh("w164-rem.vec")
    rem_dirs = [(PFIVE, PTHREE), (0xC014000000000000, PTHREE),
                (PFIVE, 0xC008000000000000), (0x401C000000000000, PTWO),
                (0x4020000000000000, PTWO), (PONE, PTWO), (PTHREE, PTWO),
                (0x400C000000000000, PONE), (PMAX, PONE), (PMIN_S, PONE),
                (PONE, PMAX), (PZERO, PONE), (NZERO, PONE), (PONE, PINF),
                (PZERO, PINF), (PINF, PONE), (PONE, PZERO), (PINF, PINF),
                (PZERO, PZERO), (QNAN, PONE), (PONE, SNAN), (SNAN, QNAN),
                (PMIN_S, PMIN_S), (PMAX_S, PMIN_S), (PTHREE, P1P5)]
    for (x, y) in rem_dirs:
        r, fl = ref_rem(x, y)
        put(f, "w164-rem.vec", "msf64_remainder", "-", [hx(x), hx(y)],
            r, fl, "rem-dir")
    for _ in range(900):
        x = rnorm64(rng)
        y = rnorm64(rng) if rng.random() < 0.95 else rsub64(rng)
        r, fl = ref_rem(x, y)
        put(f, "w164-rem.vec", "msf64_remainder", "-", [hx(x), hx(y)],
            r, fl, "rem-rand")
    f.close()

    # roundToIntegral 6 forms
    f = fh("w164-rint.vec")
    rint_pool = [PZERO, NZERO, PONE, NONE, PHALF, 0xBFF0000000000000,
                 P1P5, N1P5, 0x4004000000000000, 0xC004000000000000,
                 0x4059000000000000, 0xC059000000000000, PMAX, PMIN_S,
                 PMIN_N, PINF, NINF, QNAN, SNAN, 0x3FF0000000000001,
                 0x3FEFFFFFFFFFFFFF, 0x4330000000000000]
    named = ["ties_to_even", "ties_to_away", "toward_zero",
             "toward_positive", "toward_negative"]
    for m in named:
        for a in rint_pool:
            r, fl = ref_rint(a, m, False, "te")
            put(f, "w164-rint.vec", "msf64_round_to_integral_" + m, "-",
                [hx(a)], r, fl, "rint")
    for rm in RMS:
        for a in rint_pool:
            r, fl = ref_rint(a, "te", True, rm)
            put(f, "w164-rint.vec", "msf64_round_to_integral_exact", rm,
                [hx(a)], r, fl, "rint-exact")
        for _ in range(40):
            a = rnorm64(rng)
            r, fl = ref_rint(a, "te", True, rm)
            put(f, "w164-rint.vec", "msf64_round_to_integral_exact", rm,
                [hx(a)], r, fl, "rint-exact-rand")
    f.close()

    # nextUp/Down over boundaries
    f = fh("w164-next.vec")
    nx_pool = [PZERO, NZERO, PONE, PMIN_S, NMIN_S, PMAX_S, NMAX_S,
               PMIN_N, NMIN_N, PMAX, NMAX, PINF, NINF, QNAN, SNAN,
               SNAN_N, 0x3FF0000000000001, 0x7FEFFFFFFFFFFFFF,
               0x0010000000000001, 0x800FFFFFFFFFFFFF]
    for up, op in [(True, "msf64_next_up"), (False, "msf64_next_down")]:
        for a in nx_pool:
            r, fl = ref_next(a, up)
            put(f, "w164-next.vec", op, "-", [hx(a)], r, fl, "next")
        for _ in range(120):
            a = rnorm64(rng)
            r, fl = ref_next(a, up)
            put(f, "w164-next.vec", op, "-", [hx(a)], r, fl, "next-rand")
    f.close()

    # scaleB: x pool x N pool (incl huge, fractional-N, inf/nan N)
    f = fh("w164-scaleb.vec")
    n_pool = [0x0, 0x8000000000000000, PONE, NONE, PTWO,
              0xC008000000000000, 0x4059000000000000,
              0xC059000000000000, 0x4330000000000000,
              0xC330000000000000, 0x3FF8000000000000,
              0xBFF8000000000000, PINF, NINF, QNAN, SNAN,
              0x408ECC0000000000, 0xC08ECC0000000000,
              0x7FEFFFFFFFFFFFFF, 0x0010000000000000,
              0x0000000000000001, 0x8000000000000001]
    x_pool = [PONE, PHALF, PMAX_S, PMIN_S, NMIN_S, PMAX, PMIN_N,
              PZERO, NZERO, PINF, NINF, QNAN, SNAN,
              0x3FF0000000000001, 0x7FEFFFFFFFFFFFFF,
              0x0010000000000001, 0x000FFFFFFFFFFFFF,
              0x4008000000000000, 0xC008000000000000,
              0x3FE0000000000000]
    for rm in RMS:
        for x in x_pool:
            for n in n_pool:
                r, fl = ref_scaleb(x, n, rm)
                put(f, "w164-scaleb.vec", "msf64_scale_b", rm,
                    [hx(x), hx(n)], r, fl, "scaleb")
    f.close()

    # logB over specials + randoms
    f = fh("w164-logb.vec")
    for a in nx_pool + [PMAX_S, NMAX_S, 0x3FF0000000000000,
                        0x4000000000000000, 0x0000000000000002]:
        r, fl = ref_logb(a)
        put(f, "w164-logb.vec", "msf64_log_b", "-", [hx(a)], r, fl,
            "logb")
    for _ in range(120):
        a = rnorm64(rng)
        r, fl = ref_logb(a)
        put(f, "w164-logb.vec", "msf64_log_b", "-", [hx(a)], r, fl,
            "logb-rand")
    f.close()

    # from-int 8 widths x boundary values x 4 modes
    f = fh("w164-fromint.vec")
    for (w, sg) in INT_WIDTHS:
        tag = ("i" if sg else "u") + str(w)
        if w == 8:
            vals = [0x00, 0x01, 0x7F, 0x80, 0xFF, 0x7E, 0x81, 0x02,
                    0xFE, 0x40, 0xC0, 0x55, 0xAA, 0x10]
        elif w == 16:
            vals = [0x0, 0x1, 0x7FFF, 0x8000, 0xFFFF, 0x7FFE, 0x8001,
                    0x100, 0xFF00, 0x1234, 0xABCD, 0x5555, 0x8001, 0x7F00]
        elif w == 32:
            vals = [0x0, 0x1, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF,
                    0x7FFFFFFE, 0x80000001, 0x1000000, 0xFFFFFFFF - 1,
                    0x12345678, 0xDEADBEEF & 0xFFFFFFFF, 0x55555555,
                    0x80000000 + 1, 0x7FFFFF00]
        else:
            vals = [0x0, 0x1, 0x7FFFFFFFFFFFFFFF, 0x8000000000000000,
                    0xFFFFFFFFFFFFFFFF, 0x7FFFFFFFFFFFFFFE,
                    0x8000000000000001, 0x1000000000000,
                    0xFFFFFFFFFFFFFFFE, 0x123456789ABCDEF0,
                    0xDEADBEEFDEADBEEF & 0xFFFFFFFFFFFFFFFF,
                    0x5555555555555555, 0x1FFFFFFFFFFFFF, 0x20000000000000]
        for rm in RMS:
            for n in vals:
                r, fl = ref_from_int(n, w, sg, rm)
                put(f, "w164-fromint.vec", "msf64_from_" + tag, rm,
                    [hx(n)], r, fl, "fromint")
    f.close()

    # to-int: 10 variants x 8 widths x boundary/fraction/inf/nan
    f = fh("w164-toint.vec")
    to_pool = [PZERO, NZERO, 0x3FE0000000000000, 0xBFE0000000000000,
               0x3FF8000000000000, 0xBFF8000000000000,
               0x4004000000000000, 0xC004000000000000,
               0x4059000000000000, 0xC059000000000000,
               0x4060000000000000, 0xC060000000000000,
               0x4330000000000000, 0xC330000000000000,
               PINF, NINF, QNAN, SNAN, PMIN_S, PMAX]
    for (w, sg) in INT_WIDTHS:
        tag = ("i" if sg else "u") + str(w)
        for m in INT_MODES:
            for exact in [False, True]:
                op = "msf64_to_" + tag + ("_exact_" if exact else "_") + m
                for a in to_pool:
                    r, fl = ref_to_int(a, w, sg, m, exact)
                    put(f, "w164-toint.vec", op, "-", [hx(a)],
                        hx(r, w), fl, "toint")
    f.close()

    # NaN matrix incl payload conversion + FMA ruling + saturation
    f = fh("w164-nan.vec")
    nan_ops = [PONE, PZERO, PINF, PMAX, PMIN_S]
    for rm in ["te", "tn"]:
        for q in [QNAN, QNAN_N, QNAN_P1, QNAN_BIG, QNAN_MAX, SNAN,
                  SNAN_N, SNAN_P]:
            for w in nan_ops:
                for op, fn in [("msf64_add", lambda a, b: ref_addsub(
                        a, b, False, False, False, rm)),
                               ("msf64_mul", lambda a, b: ref_mul(
                                   a, b, False, False, rm)),
                               ("msf64_div", lambda a, b: ref_div(
                                   a, b, False, False, rm))]:
                    r, fl = fn(q, w)
                    put(f, "w164-nan.vec", op, rm, [hx(q), hx(w)], r,
                        fl, "nan-first")
                    r, fl = fn(w, q)
                    put(f, "w164-nan.vec", op, rm, [hx(w), hx(q)], r,
                        fl, "nan-second")
                r, fl = ref_sqrt(q, rm)
                put(f, "w164-nan.vec", "msf64_sqrt", rm, [hx(q)], r, fl,
                    "nan-sqrt")
                for c in [QNAN, PONE, PINF]:
                    r, fl = ref_fma(PZERO, PINF, c, False, False, False,
                                    rm)
                    put(f, "w164-nan.vec", "msf64_fma", rm,
                        [hx(PZERO), hx(PINF), hx(c)], r, fl, "nan-ruling")
    # f32 -> f64 payload widening incl quieting
    for rm in RMS:
        for b in F_SPECIALS:
            r, fl = ref_from_f32(b, rm)
            put(f, "w164-nan.vec", "msf64_from_f32", rm, [hx(b)], r, fl,
                "nan-wide")
    f.close()

    # convertFormat directed + random
    f = fh("w164-conv.vec")
    for rm in RMS:
        for b in F_SPECIALS:
            r, fl = ref_from_f32(b, rm)
            put(f, "w164-conv.vec", "msf64_from_f32", rm, [hx(b)], r,
                fl, "conv32")
        for _ in range(100):
            b = rnorm32(rng) if rng.random() < 0.9 else rsub32(rng)
            r, fl = ref_from_f32(b, rm)
            put(f, "w164-conv.vec", "msf64_from_f32", rm, [hx(b)], r,
                fl, "conv32-rand")
        for a in D_SPECIALS:
            r, fl = ref_from_f64(a, rm)
            put(f, "w164-conv.vec", "msf64_from_f64", rm, [hx(a)], r,
                fl, "conv64")
        for _ in range(50):
            a = rnorm64(rng)
            r, fl = ref_from_f64(a, rm)
            put(f, "w164-conv.vec", "msf64_from_f64", rm, [hx(a)], r,
                fl, "conv64-rand")
    f.close()

    total = sum(counts.values())
    print("exact-w164 files:")
    for k in sorted(counts):
        print("  %s %d" % (k, counts[k]))
    print("  TOTAL %d" % total)


main()
