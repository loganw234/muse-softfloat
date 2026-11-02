#!/usr/bin/env python3
"""Verifier-w1f32 probe 3: INDEPENDENT exact-rational reference for the
project-exact wave-1 binary32 families. Written fresh for verification;
not imported from tests/gen_vectors_f32.py. Rules from S1/report.md and
SF-0 (cited by clause in the verifier report); project rulings follow the
SF-0 2.5 NaN matrix and the header/summary records in the copy.
Emits .vec files replayed by the copy's own runner (exact compare).
"""
import sys
from fractions import Fraction

INV, DIV0, OVF, UNF, INX = 0x01, 0x02, 0x04, 0x08, 0x10
RMS = ["te", "tz", "tp", "tn"]

def consts(fmt):
    if fmt == "f32":
        bits, p, w = 32, 24, 8
    else:
        bits, p, w = 64, 53, 11
    t = bits - 1 - w
    emax = (1 << (w - 1)) - 1
    return {"bits": bits, "p": p, "w": w, "t": t, "emax": emax,
            "emin": 1 - emax, "bias": emax, "sign": 1 << (bits - 1),
            "expmax": (1 << w) - 1, "fracmask": (1 << t) - 1,
            "quiet": 1 << (t - 1), "inf": ((1 << w) - 1) << t}

class D:
    def __init__(self, fmt, bits):
        c = consts(fmt)
        self.fmt, self.bits = fmt, bits
        self.sign = 1 if bits & c["sign"] else 0
        e = (bits >> c["t"]) & c["expmax"]
        self.frac = bits & c["fracmask"]
        if e == c["expmax"]:
            self.sig, self.exp = self.frac, 0
            self.cls = "inf" if self.frac == 0 else ("qnan" if self.frac & c["quiet"] else "snan")
        elif e == 0:
            self.sig, self.exp = self.frac, c["emin"] - c["t"]
            self.cls = "zero" if self.frac == 0 else "finite"
        else:
            self.sig, self.exp = self.frac | (1 << c["t"]), e - c["bias"] - c["t"]
            self.cls = "finite"

    def val(self):
        if self.exp >= 0:
            v = Fraction(self.sig << self.exp)
        else:
            v = Fraction(self.sig, 1 << (-self.exp))
        return -v if self.sign else v

def dqnan(fmt):
    c = consts(fmt)
    return c["inf"] | c["quiet"]

def narrow(fmt, src):
    dc, sc = consts(fmt), consts(src.fmt)
    if dc["t"] >= sc["t"]:
        pay = src.frac << (dc["t"] - sc["t"])
    else:
        pay = src.frac >> (sc["t"] - dc["t"])
    if pay == 0:
        return dqnan(fmt)
    return (dc["sign"] if src.sign else 0) | dc["inf"] | pay | dc["quiet"]

def nan_deliver(fmt, ops, inv_wo_nan):
    for d in ops:
        if d.cls == "snan":
            return narrow(fmt, d), INV
    for d in ops:
        if d.cls == "qnan":
            return narrow(fmt, d), 0
    if inv_wo_nan:
        return dqnan(fmt), INV
    return None, 0

def flog2(m):
    e = m.numerator.bit_length() - m.denominator.bit_length()
    if e >= 0:
        if m.numerator < (m.denominator << e):
            e -= 1
    else:
        if (m.numerator << (-e)) < m.denominator:
            e -= 1
    return e

def round_f32(sign, mag, rm):
    """Round exact magnitude to f32 once (Clauses 4.3, 7; tininess after
    rounding per 7.5: unbounded-precision rounding judged vs 2^emin)."""
    c = consts("f32")
    p, emax, emin = c["p"], c["emax"], c["emin"]
    if mag == 0:
        return (c["sign"] if sign else 0), 0
    e = flog2(mag)
    scale = max(e, emin) - (p - 1)
    num, den = mag.numerator, mag.denominator
    if scale >= 0:
        den <<= scale
    else:
        num <<= -scale
    q, r = divmod(num, den)
    inx = r != 0
    if inx:
        t2 = 2 * r
        if rm == "te":
            inc = t2 > den or (t2 == den and q & 1)
        elif rm == "tp":
            inc = not sign
        elif rm == "tn":
            inc = bool(sign)
        else:
            inc = False  # tz
        if inc:
            q += 1
    if q == (1 << p):
        q >>= 1
        scale += 1
    tiny = False
    if e < emin and inx:
        su = e - (p - 1)
        nu, du = mag.numerator, mag.denominator
        if su >= 0:
            du <<= su
        else:
            nu <<= -su
        qu, ru = divmod(nu, du)
        if ru:
            t2 = 2 * ru
            if rm == "te":
                bump = t2 > du or (t2 == du and qu & 1)
            elif rm == "tp":
                bump = not sign
            elif rm == "tn":
                bump = bool(sign)
            else:
                bump = False
            if bump:
                qu += 1
        if qu == (1 << p):
            qu >>= 1
            su += 1
        tiny = Fraction(qu, 1) * (Fraction(1 << su) if su >= 0 else Fraction(1, 1 << (-su))) < Fraction(2) ** emin
    sb = c["sign"] if sign else 0
    if q >= (1 << (p - 1)):
        big = scale + (p - 1)
        if big > emax:
            to_inf = rm == "te" or (rm == "tp" and not sign) or (rm == "tn" and sign)
            enc = c["inf"] if to_inf else ((c["expmax"] - 1) << c["t"]) | c["fracmask"]
            return sb | enc, OVF | INX
        fl = INX | (UNF if tiny else 0) if inx else 0
        return sb | ((big + c["bias"]) << c["t"]) | (q - (1 << (p - 1))), fl
    fl = INX | (UNF if tiny else 0) if inx else 0
    return sb | q, fl


def ref_addsub(af, a, bf, b, issub, rm):
    da, db = D(af, a), D(bf, b)
    eff = db.sign ^ (1 if issub else 0)
    inv = da.cls == "inf" and db.cls == "inf" and da.sign != eff
    o, f = nan_deliver("f32", [da, db], inv)
    if o is not None:
        return o, f
    if da.cls == "inf":
        return (consts("f32")["sign"] if da.sign else 0) | consts("f32")["inf"], 0
    if db.cls == "inf":
        return (consts("f32")["sign"] if eff else 0) | consts("f32")["inf"], 0
    ex = (da.val() - db.val()) if issub else (da.val() + db.val())
    if ex == 0:
        if da.val() == 0 and db.val() == 0 and da.sign == eff:
            return (consts("f32")["sign"] if da.sign else 0), 0
        return (consts("f32")["sign"] if rm == "tn" else 0), 0
    return round_f32(ex < 0, abs(ex), rm)


def ref_mul(af, a, bf, b, rm):
    da, db = D(af, a), D(bf, b)
    s = da.sign ^ db.sign
    inv = (da.cls == "zero" and db.cls == "inf") or (da.cls == "inf" and db.cls == "zero")
    o, f = nan_deliver("f32", [da, db], inv)
    if o is not None:
        return o, f
    if da.cls == "inf" or db.cls == "inf":
        return (consts("f32")["sign"] if s else 0) | consts("f32")["inf"], 0
    if da.cls == "zero" or db.cls == "zero":
        return (consts("f32")["sign"] if s else 0), 0
    return round_f32(s, abs(da.val() * db.val()), rm)


def ref_div(af, a, bf, b, rm):
    da, db = D(af, a), D(bf, b)
    s = da.sign ^ db.sign
    inv = (da.cls == "zero" and db.cls == "zero") or (da.cls == "inf" and db.cls == "inf")
    o, f = nan_deliver("f32", [da, db], inv)
    if o is not None:
        return o, f
    if da.cls == "inf":
        return (consts("f32")["sign"] if s else 0) | consts("f32")["inf"], 0
    if db.cls == "inf":
        return (consts("f32")["sign"] if s else 0), 0
    if db.cls == "zero":
        return (consts("f32")["sign"] if s else 0) | consts("f32")["inf"], DIV0
    if da.cls == "zero":
        return (consts("f32")["sign"] if s else 0), 0
    q = da.val() / db.val()
    return round_f32(q < 0, abs(q), rm)


def ref_sqrt(af, a, rm):
    from math import isqrt
    da = D(af, a)
    inv = bool(da.sign) and da.cls in ("inf", "finite")
    o, f = nan_deliver("f32", [da], inv)
    if o is not None:
        return o, f
    if da.cls == "inf":
        return consts("f32")["inf"], 0
    if da.cls == "zero":
        return (consts("f32")["sign"] if da.sign else 0), 0
    v = da.val()
    n, d = v.numerator, v.denominator
    e = flog2(v) // 2
    c = consts("f32")
    p, emin, emax = c["p"], c["emin"], c["emax"]
    scale = max(e, emin) - (p - 1)
    # u = sqrt(v) / 2^(scale-2); u^2 = N/Dd with integers below
    if 4 - 2 * scale >= 0:
        N, Dd = n << (4 - 2 * scale), d
    else:
        N, Dd = n, d << (2 * scale - 4)
    S = isqrt(N * Dd)
    exact = (S * S == N * Dd)
    fl = S // Dd
    below = (S % Dd) != 0
    guard, rbit, cand = (fl >> 1) & 1, fl & 1, fl >> 2
    stick = below or not exact
    inx = guard or rbit or stick
    inc = False
    if inx:
        if rm == "te":
            inc = guard and (rbit or stick or (cand & 1))
        elif rm == "tp":
            inc = True  # sqrt result non-negative; tp rounds up iff inexact
        elif rm == "tn":
            inc = False
        if inc:
            cand += 1
    if cand == (1 << p):
        cand >>= 1
        scale += 1
    tiny = False
    if e < emin and inx:
        # unbounded-precision rounding vs 2^emin
        su = e - (p - 1)
        if 4 - 2 * su >= 0:
            Nu, Du = n << (4 - 2 * su), d
        else:
            Nu, Du = n, d << (2 * su - 4)
        Su = isqrt(Nu * Du)
        qu = Su // Du
        remu, tailu = Su % Du, (Su * Su != Nu * Du)
        if remu or tailu:
            if rm == "tp":
                qu += 1
            elif rm == "te" and (2 * remu > Du or (2 * remu == Du and (tailu or qu & 1))):
                qu += 1
        if qu == (1 << p):
            qu >>= 1
            su += 1
        tiny = Fraction(qu) * (Fraction(1 << su) if su >= 0 else Fraction(1, 1 << (-su))) < Fraction(2) ** emin
    sb = 0
    if cand >= (1 << (p - 1)):
        big = scale + (p - 1)
        if big > emax:
            enc = c["inf"] if rm in ("te", "tp") else ((c["expmax"] - 1) << c["t"]) | c["fracmask"]
            return sb | enc, OVF | INX
        fl2 = INX | (UNF if tiny else 0) if inx else 0
        return sb | ((big + c["bias"]) << c["t"]) | (cand - (1 << (p - 1))), fl2
    fl2 = INX | (UNF if tiny else 0) if inx else 0
    return sb | cand, fl2


def ref_fma(af, a, bf, b, cf, c, rm):
    da, db, dc = D(af, a), D(bf, b), D(cf, c)
    ps = da.sign ^ db.sign
    zxi = (da.cls == "zero" and db.cls == "inf") or (da.cls == "inf" and db.cls == "zero")
    pinf = (da.cls == "inf" and db.cls not in ("snan", "qnan") and db.cls != "zero") or \
           (db.cls == "inf" and da.cls not in ("snan", "qnan") and da.cls != "zero")
    inv = zxi or (pinf and dc.cls == "inf" and ps != dc.sign)
    extra = INV if (zxi and dc.cls == "qnan") else 0
    o, f = nan_deliver("f32", [da, db, dc], inv)
    if o is not None:
        return o, extra | f
    if pinf:
        return (consts("f32")["sign"] if ps else 0) | consts("f32")["inf"], 0
    if dc.cls == "inf":
        return (consts("f32")["sign"] if dc.sign else 0) | consts("f32")["inf"], 0
    prod = Fraction(0) if (da.cls == "zero" or db.cls == "zero") else da.val() * db.val()
    ex = prod if dc.cls == "zero" else prod + dc.val()
    if ex == 0:
        # Clause 6.3 zero sum: addend-zero and product-zero signs
        if (da.cls == "zero" or db.cls == "zero") and dc.cls == "zero":
            samesign = (ps == dc.sign)
            s = ps if samesign else (rm == "tn")
            return (consts("f32")["sign"] if s else 0), 0
        return (consts("f32")["sign"] if rm == "tn" else 0), 0
    return round_f32(ex < 0, abs(ex), rm)


def round_int_mag(sig, exp, sign, mode):
    """Round exact sig*2^exp to integer magnitude; return (q, frac)."""
    if sig == 0:
        return 0, False
    if exp >= 0:
        return sig << exp, False
    sh = -exp
    q = 0 if sh >= 256 else sig >> sh
    mask = (1 << sh) - 1 if sh < 256 else None
    frac = (sig & mask) != 0 if mask is not None else sig != 0
    if not frac:
        return q, False
    half = bool((sig >> (sh - 1)) & 1) if 1 <= sh - 1 < 256 else (False if sh - 1 < 1 else True)
    below = (sig & ((1 << (sh - 1)) - 1)) != 0 if 1 < sh - 1 < 256 else (False if sh - 1 <= 1 else sig != 0)
    inc = False
    if mode == "te":
        inc = half and (below or q & 1)
    elif mode == "ta":
        inc = half
    elif mode == "tp":
        inc = not sign
    elif mode == "tn":
        inc = bool(sign)
    return (q + 1 if inc else q), True


def ref_rint(a, mode, exact_form):
    da = D("f32", a)
    o, f = nan_deliver("f32", [da], False)
    if o is not None:
        return o, f
    if da.cls in ("inf", "zero") or da.exp >= 0:
        return a, 0
    q, frac = round_int_mag(da.sig, da.exp, da.sign, mode)
    bits, _ = round_f32(da.sign, Fraction(q), "te")
    return bits, (INX if (exact_form and frac) else 0)


def ref_next(a, up):
    da = D("f32", a)
    o, f = nan_deliver("f32", [da], False)
    if o is not None:
        return o, f
    if da.cls == "inf":
        if up:
            return (0xFF7FFFFF if da.sign else a), 0
        return (a if da.sign else 0x7F7FFFFF), 0
    if da.cls == "zero":
        return (1 if up else 0x80000001), 0
    if up:
        return (a - 1 if da.sign else a + 1) & 0xFFFFFFFF, 0
    return (a + 1 if da.sign else a - 1) & 0xFFFFFFFF, 0


def ref_remainder(a, b):
    da, db = D("f32", a), D("f32", b)
    inv = da.cls == "inf" or db.cls == "zero"
    o, f = nan_deliver("f32", [da, db], inv)
    if o is not None:
        return o, f
    if db.cls == "inf" or da.cls == "zero":
        return a, 0
    x, y = da.val(), db.val()
    ax, ay = abs(x), abs(y)
    n = ax // ay
    r = ax - n * ay
    t2 = 2 * r
    if t2 > ay or (t2 == ay and n & 1):
        n += 1
    diff = ax - n * ay
    if diff == 0:
        return (consts("f32")["sign"] if da.sign else 0), 0
    # true result is sign(x) * diff (Clause 6: remainder takes sign of x
    # combined with the correction direction)
    rsign = da.sign ^ (1 if diff < 0 else 0)
    return round_f32(rsign, abs(diff), "te")


def ref_scaleb(a, nbits, rm):
    x, nb = D("f32", a), D("f64", nbits)
    o, f = nan_deliver("f32", [x, nb], False)
    if o is not None:
        return o, f
    if x.cls in ("inf", "zero"):
        return a, 0
    if nb.cls == "zero":
        return a, 0
    if nb.cls == "inf":
        ni = 10000 if not nb.sign else -10000
        return round_f32(x.sign, abs(x.val()) * Fraction(2) ** ni if ni > 0 else abs(x.val()) / Fraction(2) ** (-ni), rm)
    # project ruling: non-integral N truncates toward zero
    nv = nb.val()
    ni = int(nv) if nv >= 0 else -int(-nv)
    if ni >= 10000:
        return round_f32(x.sign, abs(x.val()) * (Fraction(2) ** 10000), rm)
    if ni <= -10000:
        return round_f32(x.sign, abs(x.val()) / (Fraction(2) ** 10000), rm)
    if ni >= 0:
        return round_f32(x.sign, abs(x.val()) * (Fraction(2) ** ni), rm)
    return round_f32(x.sign, abs(x.val()) / (Fraction(2) ** (-ni)), rm)


def int_to_f64_bits(e):
    """Exact encoding of a small integer (|e| < 2^52) as f64 bits."""
    if e == 0:
        return 0

    c64 = consts("f64")
    s = 1 if e < 0 else 0
    m = -e if s else e
    bl = m.bit_length()
    assert 1 <= bl <= 52
    ef = (bl - 1) + c64["bias"]
    frac = (m - (1 << (bl - 1))) << (c64["t"] - bl + 1)
    return (c64["sign"] if s else 0) | (ef << c64["t"]) | frac


def ref_logb(a):
    da = D("f32", a)
    o, f = nan_deliver("f64", [da], False)
    if o is not None:
        return o, f
    c64 = consts("f64")
    if da.cls == "zero":
        return c64["sign"] | c64["inf"], DIV0
    if da.cls == "inf":
        return c64["inf"], 0
    # unbiased exponent of |x|: position of top significand bit
    e = (da.sig.bit_length() - 1) + da.exp
    return int_to_f64_bits(e), 0


def ref_from_int(sign, mag, rm):
    return round_f32(sign, Fraction(mag), rm)


def to_limits(signed, width):
    if width == 64:
        return (0x7FFFFFFFFFFFFFFF, 0x8000000000000000) if signed else (0xFFFFFFFFFFFFFFFF, 0)
    if signed:
        return ((1 << (width - 1)) - 1, 1 << (width - 1))
    return ((1 << width) - 1, 0)


def ref_to_int(a, signed, width, mode, exact_form):
    da = D("f32", a)
    mx, mn = to_limits(signed, width)
    if da.cls in ("snan", "qnan"):
        return 0, INV
    if da.cls == "inf":
        return (mn if da.sign else mx), INV
    q, frac = round_int_mag(da.sig, da.exp, da.sign, mode)
    if q == 0:
        return 0, (INX if (exact_form and frac) else 0)
    if da.sign:
        lim = mn if signed else 0
        if (not signed) or q > lim:
            return lim, INV
        return (((1 << width) - q) & ((1 << width) - 1)), (INX if (exact_form and frac) else 0)
    if q > mx:
        return mx, INV
    return q, (INX if (exact_form and frac) else 0)


# predicate table: name -> (mask over REL_LT/EQ/GT/UN, signaling?)
RL, RE, RG, RU = 1, 2, 4, 8
PREDS = {
    "quiet_equal": (RE, 0), "quiet_not_equal": (RL | RG | RU, 0),
    "signaling_equal": (RE, 1), "signaling_not_equal": (RL | RG | RU, 1),
    "quiet_greater": (RG, 0), "quiet_greater_equal": (RG | RE, 0),
    "quiet_less": (RL, 0), "quiet_less_equal": (RL | RE, 0),
    "quiet_not_greater": (RL | RE | RU, 0), "quiet_not_less": (RG | RE | RU, 0),
    "quiet_less_unordered": (RL | RU, 0), "quiet_greater_unordered": (RG | RU, 0),
    "quiet_unordered": (RU, 0), "quiet_ordered": (RL | RE | RG, 0),
    "signaling_greater": (RG, 1), "signaling_greater_equal": (RG | RE, 1),
    "signaling_less": (RL, 1), "signaling_less_equal": (RL | RE, 1),
    "signaling_not_greater": (RL | RE | RU, 1), "signaling_not_less": (RG | RE | RU, 1),
    "signaling_less_unordered": (RL | RU, 1), "signaling_greater_unordered": (RG | RU, 1),
}


def ref_cmp(af, a, bf, b, pred):
    mask, sig = PREDS[pred]
    da, db = D(af, a), D(bf, b)
    an, bn = da.cls in ("snan", "qnan"), db.cls in ("snan", "qnan")
    if an or bn:
        rel = RU
        fl = INV if (da.cls == "snan" or db.cls == "snan" or sig) else 0
    elif da.cls == "inf" or db.cls == "inf":
        if da.cls == "inf" and db.cls == "inf":
            rel = RE if da.sign == db.sign else (RL if da.sign else RG)
        elif da.cls == "inf":
            rel = RL if da.sign else RG
        else:
            rel = RG if db.sign else RL
        fl = 0
    else:
        va, vb = da.val(), db.val()
        rel = RL if va < vb else (RG if va > vb else RE)
        fl = 0
    return (1 if mask & rel else 0), fl


def to_key_class(a):
    """Class skeleton rank for totalOrder (Clause 5.10 as extracted in S1):
    -qnan < -snan < -inf < -finite < -0 < +0 < +finite < +inf < +snan < +qnan."""
    da = D("f32", a)
    if da.cls == "qnan":
        return (0 if da.sign else 9), 0
    if da.cls == "snan":
        return (1 if da.sign else 8), 0
    if da.cls == "inf":
        return (2 if da.sign else 7), 0
    if da.cls == "zero":
        return (4 if da.sign else 5), 0
    return (3 if da.sign else 6), 1  # finite: needs magnitude order


def ref_total_order(a, b):
    ka, fa = to_key_class(a)
    kb, fb = to_key_class(b)
    if ka != kb:
        return (1 if ka < kb else 0), None  # decided by skeleton
    if not fa:
        return "PAYLOAD", None  # same NaN class: payload direction undecided by S1/SF-0
    da, db = D("f32", a), D("f32", b)
    va, vb = abs(da.val()), abs(db.val())
    if ka in (3,):  # negative finite: larger magnitude first
        return (1 if va >= vb else 0), None
    if va == vb and ka == 4 or ka == 5:
        return 1, None
    return (1 if va <= vb else 0), None
