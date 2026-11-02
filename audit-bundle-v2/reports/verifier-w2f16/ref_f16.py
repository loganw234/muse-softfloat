"""Independent f16 exact reference for verifier-w2f16 (probe 5/6).

Fresh code: Fraction/integer arithmetic only, no imports from
tests/gen_vectors*.py or any parcel/oracle code. IEEE 754-2019 intent:
single rounding via one pack, tininess detected after rounding
(house 8086-SSE rule), NaN narrow truncation keeps top payload bits.
"""
from fractions import Fraction

P = 11
EMAX = 15
EMIN = -14
NX, UF, OF, DZ, NV = 0x10, 0x08, 0x04, 0x02, 0x01

QBIT = 1 << 9


def pow2(n):
    if n >= 0:
        return Fraction(1 << n, 1)
    return Fraction(1, 1 << (-n))


def dec(u):
    s = (u >> 15) & 1
    e = (u >> 10) & 0x1F
    f = u & 0x3FF
    if e == 0x1F:
        return {"s": s, "cls": "snan" if not (f & QBIT) and f else
                ("qnan" if f else "inf"), "pay": f & 0x3FF, "enc": u}
    if e == 0:
        v = Fraction(f, 1 << 24)
    else:
        v = Fraction((1 << 10) + f, 1 << 10) * (Fraction(2) ** (e - 15))
    if v == 0:
        return {"s": s, "cls": "zero", "v": Fraction(0), "enc": u}
    return {"s": s, "cls": "fin", "v": v if s == 0 else -v, "enc": u}


def is_nan_d(u):
    e = (u >> 10) & 0x1F
    return e == 0x1F and (u & 0x3FF) != 0


def is_snan_d(u):
    return is_nan_d(u) and not (u & QBIT)


def round_f16(mag, sign, rm):
    """mag >= 0 Fraction. Returns (enc16, flags)."""
    assert mag >= 0
    if mag == 0:
        return (sign << 15), 0
    e = mag.numerator.bit_length() - mag.denominator.bit_length()
    if mag < pow2(e):
        e -= 1
    if e >= EMIN:
        unit_exp = e - (P - 1)
        scaled = mag / pow2(unit_exp)
        q0 = int(scaled)
        frac = scaled - q0
        rbit, sticky = divmod(frac * 2, 1)
        rbit = int(rbit)
        sticky = int(sticky != 0)
        up = round_decision(q0, rbit, sticky, rm, sign)
        q0 += 1 if up else 0
        if q0 >= (1 << P):
            q0 >>= 1
            e += 1
        inexact = (frac != 0)
        tiny = False
        if e > EMAX:
            return overflow(sign, rm)
        enc = (sign << 15) | ((e + 15) << 10) | (q0 - (1 << (P - 1)))
        fl = NX if inexact else 0
        return enc, fl
    q = mag * (1 << (10 - EMIN))
    q0 = int(q)
    frac = q - q0
    rbit = int((frac * 2) >= 1)
    sticky = int((frac * 2 - rbit) != 0)
    up = round_decision(q0, rbit, sticky, rm, sign)
    q0 += 1 if up else 0
    inexact = (frac != 0)
    if q0 >= (1 << (P - 1)):
        enc = (sign << 15) | ((EMIN + 15) << 10) | (q0 - (1 << (P - 1)))
        fl = NX if inexact else 0
        return enc, fl
    if q0 == 0:
        enc = sign << 15
    else:
        enc = (sign << 15) | q0
    fl = (NX if inexact else 0) | (UF if inexact else 0)
    return enc, fl


def round_decision(q0, rbit, sticky, rm, sign):
    if rm == "tz":
        return False
    if rm == "tp":
        return sign == 0 and (rbit or sticky)
    if rm == "tn":
        return sign == 1 and (rbit or sticky)
    if rm == "ta":
        return bool(rbit)
    if rbit == 0:
        return False
    if sticky:
        return True
    return (q0 & 1) == 1


def overflow(sign, rm):
    to_inf = (rm == "te" or rm == "ta" or
              (rm == "tp" and sign == 0) or (rm == "tn" and sign == 1))
    if to_inf:
        return (sign << 15) | (0x1F << 10), OF | NX
    return (sign << 15) | (0x1E << 10) | 0x3FF, OF | NX


def nan_default(sign):
    return (sign << 15) | (0x1F << 10) | QBIT


def arith_nan(ax, ay):
    """(result_enc_or_None_if_finite, invalid). sNaN->invalid+default qNaN."""
    if is_snan_d(ax["enc"]) or is_snan_d(ay["enc"]):
        s = ax["s"] if is_snan_d(ax["enc"]) else ay["s"]
        return nan_default(s), NV
    if is_nan_d(ax["enc"]):
        return None, 0
    if is_nan_d(ay["enc"]):
        return None, 0
    return None, 0


def op_add(a, b, rm):
    ax, ay = dec(a), dec(b)
    if ax["cls"] in ("qnan", "snan") or ay["cls"] in ("qnan", "snan"):
        r, fl = arith_nan(ax, ay)
        if r is not None:
            return r, fl
        winner = ax if is_nan_d(ax["enc"]) else ay
        return winner["enc"], (NV if is_snan_d(winner["enc"]) else 0)
    if ax["cls"] == "inf" or ay["cls"] == "inf":
        if ax["cls"] == "inf" and ay["cls"] == "inf" and ax["s"] != ay["s"]:
            return nan_default(0), NV
        s = ax["s"] if ax["cls"] == "inf" else ay["s"]
        return (s << 15) | (0x1F << 10), 0
    v = ax["v"] + ay["v"]
    if v == 0:
        s = 1 if (rm == "tn" and False) else 0
        if ax["enc"] in (0x0000, 0x8000) and ay["enc"] in (0x0000, 0x8000):
            if ax["s"] == 1 and ay["s"] == 1:
                s = 1
            elif rm == "tn" and (ax["s"] == 1 or ay["s"] == 1):
                s = 1
            else:
                s = 0
        else:
            s = 1 if (rm == "tn") else 0
        return s << 15, 0
    return round_f16(abs(v), 1 if v < 0 else 0, rm)


def op_sub(a, b, rm):
    nb = b ^ 0x8000
    return op_add(a, nb, rm)


def op_mul(a, b, rm):
    ax, ay = dec(a), dec(b)
    if ax["cls"] in ("qnan", "snan") or ay["cls"] in ("qnan", "snan"):
        r, fl = arith_nan(ax, ay)
        if r is not None:
            return r, fl
        winner = ax if is_nan_d(ax["enc"]) else ay
        return winner["enc"], (NV if is_snan_d(winner["enc"]) else 0)
    s = ax["s"] ^ ay["s"]
    if (ax["cls"] == "inf" and ay["cls"] == "zero") or \
       (ay["cls"] == "inf" and ax["cls"] == "zero"):
        return nan_default(0), NV
    if ax["cls"] == "inf" or ay["cls"] == "inf":
        return (s << 15) | (0x1F << 10), 0
    v = ax["v"] * ay["v"]
    if v == 0:
        return s << 15, 0
    return round_f16(abs(v), s, rm)


def op_div(a, b, rm):
    ax, ay = dec(a), dec(b)
    if ax["cls"] in ("qnan", "snan") or ay["cls"] in ("qnan", "snan"):
        r, fl = arith_nan(ax, ay)
        if r is not None:
            return r, fl
        winner = ax if is_nan_d(ax["enc"]) else ay
        return winner["enc"], (NV if is_snan_d(winner["enc"]) else 0)
    s = ax["s"] ^ ay["s"]
    if ax["cls"] == "inf" and ay["cls"] == "inf":
        return nan_default(0), NV
    if ax["cls"] == "inf":
        return (s << 15) | (0x1F << 10), 0
    if ay["cls"] == "inf":
        return s << 15, 0
    if ay["cls"] == "zero":
        if ax["cls"] == "zero":
            return nan_default(0), NV
        return (s << 15) | (0x1F << 10), DZ
    v = ax["v"] / ay["v"]
    if v == 0:
        return s << 15, 0
    return round_f16(abs(v), s, rm)


def isqrt_rem(n):
    q = n.bit_length()
    q = (q + 1) // 2
    q = 1 << q
    while True:
        nq = (q + n // q) // 2
        if nq >= q:
            break
        q = nq
    while q * q > n:
        q -= 1
    return q, n - q * q


def op_sqrt(a, rm):
    ax = dec(a)
    if ax["cls"] in ("qnan", "snan"):
        if is_snan_d(ax["enc"]):
            return nan_default(ax["s"]), NV
        return ax["enc"], 0
    if ax["s"] == 1:
        if ax["cls"] == "zero":
            return 0x8000, 0
        return nan_default(0), NV
    if ax["cls"] == "inf":
        return 0x7C00, 0
    if ax["cls"] == "zero":
        return 0x0000, 0
    v = ax["v"]
    n, d = v.numerator, v.denominator
    K = 60
    T = n * (1 << (2 * K)) // d
    R1 = n * (1 << (2 * K)) % d
    q, r = isqrt_rem(T)
    F = Fraction(q, 1 << K)
    if r != 0 or R1 != 0:
        F += Fraction(1, 1 << (K + 2))
    return round_f16(F, 0, rm)


def op_rem(a, b):
    ax, ay = dec(a), dec(b)
    if ax["cls"] in ("qnan", "snan") or ay["cls"] in ("qnan", "snan"):
        r, fl = arith_nan(ax, ay)
        if r is not None:
            return r, fl
        winner = ax if is_nan_d(ax["enc"]) else ay
        return winner["enc"], (NV if is_snan_d(winner["enc"]) else 0)
    if ax["cls"] == "inf" or ay["cls"] == "zero":
        return nan_default(0), NV
    if ay["cls"] == "inf":
        return ax["enc"], 0
    q = ax["v"] / ay["v"]
    n = int(q)
    f = q - n
    if f > Fraction(1, 2) or (f == Fraction(1, 2) and (n & 1)):
        n += 1
    elif f < Fraction(-1, 2) or (f == Fraction(-1, 2) and (n & 1)):
        n -= 1
    r = ax["v"] - n * ay["v"]
    if r == 0:
        return (ax["s"] << 15), 0
    return round_f16(abs(r), 1 if r < 0 else 0, "te")


RINT_MODES = ("ties_to_even", "ties_to_away", "toward_zero",
              "toward_positive", "toward_negative", "exact")


def op_rint(a, mode, rm_for_exact="te"):
    ax = dec(a)
    if ax["cls"] in ("qnan", "snan"):
        if is_snan_d(ax["enc"]):
            return nan_default(ax["s"]), NV
        return ax["enc"], 0
    if ax["cls"] in ("inf", "zero"):
        return ax["enc"], 0
    v = ax["v"]
    n = int(v)
    f = v - n
    if mode == "ties_to_even":
        if f > Fraction(1, 2) or (f == Fraction(1, 2) and (n & 1)):
            n += 1
        elif f < Fraction(-1, 2) or (f == Fraction(-1, 2) and (n & 1)):
            n -= 1
    elif mode == "ties_to_away":
        if f >= Fraction(1, 2):
            n += 1
        elif f <= Fraction(-1, 2):
            n -= 1
    elif mode == "toward_zero":
        pass
    elif mode == "toward_positive":
        if f > 0:
            n += 1
    elif mode == "toward_negative":
        if f < 0:
            n -= 1
    elif mode == "exact":
        if f != 0:
            if f > Fraction(1, 2) or (f == Fraction(1, 2) and (n & 1)):
                n += 1
            elif f < Fraction(-1, 2) or (f == Fraction(-1, 2) and (n & 1)):
                n -= 1
            sgn = 1 if n < 0 else (ax["s"] if n == 0 else 0)
            enc, _ = round_f16(abs(Fraction(n, 1)), sgn, rm_for_exact)
            return enc, NX
        sgn = 1 if n < 0 else (ax["s"] if n == 0 else 0)
        enc, _ = round_f16(abs(Fraction(n, 1)), sgn, rm_for_exact)
        return enc, 0
    sgn = 1 if n < 0 else (ax["s"] if n == 0 else 0)
    enc, _ = round_f16(abs(Fraction(n, 1)), sgn, "te")
    return enc, 0


def enc_next(u, direction):
    if is_nan_d(u):
        return u, NV if is_snan_d(u) else 0
    if direction > 0:
        if u == 0x7BFF:
            return 0x7C00, 0
        if u == 0x7C00:
            return 0x7C00, 0
        if u == 0xFC00:
            return 0xFBFF, 0
        if u == 0x8000:
            return 0x0001, 0
        if u == 0x0000:
            return 0x0001, 0
        if u & 0x8000:
            return u - 1, 0
        return u + 1, 0
    if u == 0xFBFF:
        return 0xFC00, 0
    if u == 0xFC00:
        return 0xFC00, 0
    if u == 0x7C00:
        return 0x7BFF, 0
    if u == 0x0000:
        return 0x8001, 0
    if u == 0x8000:
        return 0x8001, 0
    if u & 0x8000:
        return u + 1, 0
    return u - 1, 0


def op_next_up(a):
    return enc_next(a, 1)


def op_next_down(a):
    return enc_next(a, -1)


def dec_f32(u):
    s = (u >> 31) & 1
    e = (u >> 23) & 0xFF
    f = u & 0x7FFFFF
    if e == 0xFF:
        if f == 0:
            return {"s": s, "cls": "inf", "enc": u}
        sn = not (f & 0x400000)
        return {"s": s, "cls": "snan" if sn else "qnan",
                "pay": f, "enc": u}
    if e == 0:
        v = Fraction(f, 1 << 149)
    else:
        v = Fraction((1 << 23) + f, 1 << 23) * (Fraction(2) ** (e - 127))
    if v == 0:
        return {"s": s, "cls": "zero", "v": Fraction(0), "enc": u}
    return {"s": s, "cls": "fin", "v": v if s == 0 else -v, "enc": u}


def dec_f64(u):
    s = (u >> 63) & 1
    e = (u >> 52) & 0x7FF
    f = u & 0xFFFFFFFFFFFFF
    if e == 0x7FF:
        if f == 0:
            return {"s": s, "cls": "inf", "enc": u}
        sn = not (f & 0x8000000000000)
        return {"s": s, "cls": "snan" if sn else "qnan",
                "pay": f, "enc": u}
    if e == 0:
        v = Fraction(f, 1 << 1074)
    else:
        v = Fraction((1 << 52) + f, 1 << 52) * (Fraction(2) ** (e - 1023))
    if v == 0:
        return {"s": s, "cls": "zero", "v": Fraction(0), "enc": u}
    return {"s": s, "cls": "fin", "v": v if s == 0 else -v, "enc": u}


def narrow_nan(sign, pay_full, wfull, rm_key="narrow"):
    qp = (pay_full >> (wfull - 10)) & 0x3FF
    qp |= QBIT
    return (sign << 15) | (0x1F << 10) | (qp & 0x3FF)


def op_from_f32(a, rm):
    ax = dec_f32(a)
    return _op_from(ax, 23, rm)


def op_from_f64(a, rm):
    ax = dec_f64(a)
    return _op_from(ax, 52, rm)


def op_from_f16(a, rm):
    ax = dec(a)
    return _op_from(ax, 10, rm)


def _op_from(ax, wsrc, rm):
    if ax["cls"] == "snan":
        s = ax["s"]
        pay = (ax["pay"] >> (wsrc - 10)) & 0x3FF if wsrc > 10 else ax["pay"]
        return (s << 15) | (0x1F << 10) | QBIT | pay, NV
    if ax["cls"] == "qnan":
        s = ax["s"]
        pay = (ax["pay"] >> (wsrc - 10)) & 0x3FF if wsrc > 10 else ax["pay"]
        return (s << 15) | (0x1F << 10) | QBIT | pay, 0
    if ax["cls"] == "inf":
        return (ax["s"] << 15) | (0x1F << 10), 0
    if ax["cls"] == "zero":
        return ax["s"] << 15, 0
    return round_f16(abs(ax["v"]), ax["s"], rm)


def op_scale_b(a, n64, rm):
    ax = dec(a)
    an = dec_f64(n64)
    if ax["cls"] in ("qnan", "snan"):
        if is_snan_d(ax["enc"]):
            return nan_default(ax["s"]), NV
        return ax["enc"], 0
    if an["cls"] in ("qnan", "snan"):
        return nan_default(0), NV
    if an["cls"] == "inf":
        if ax["cls"] == "zero":
            return ax["enc"], 0
        if ax["cls"] == "inf":
            return ax["enc"], 0
        s = ax["s"] ^ an["s"]
        return (s << 15) | (0x1F << 10), 0
    if ax["cls"] == "inf":
        return ax["enc"], 0
    if ax["cls"] == "zero":
        return ax["enc"], 0
    k = int(an["v"])
    if k > 100:
        return overflow(ax["s"], rm)
    if k < -100:
        outward = (rm == "tp" and ax["s"] == 0) or \
            (rm == "tn" and ax["s"] == 1)
        enc = ((ax["s"] << 15) | 0x0001) if outward else (ax["s"] << 15)
        return enc, UF | NX
    if k >= 0:
        v = ax["v"] * (1 << k)
    else:
        v = ax["v"] / (1 << (-k))
    if v == 0:
        return ax["s"] << 15, 0
    return round_f16(abs(v), 1 if v < 0 else 0, rm)


def enc_f64_int(e):
    if e == 0:
        return 0x0000000000000000
    s = 0
    if e < 0:
        s = 1
        e = -e
    exp = e.bit_length() - 1 + 1023
    man = e - (1 << (e.bit_length() - 1))
    shift = 52 - (e.bit_length() - 1)
    return (s << 63) | (exp << 52) | (man << shift)


def op_log_b(a):
    ax = dec(a)
    if ax["cls"] in ("qnan", "snan"):
        if is_snan_d(ax["enc"]):
            return (0x7FF8000000000000, NV)
        s = ax["s"]
        return ((s << 63) | (0x7FF << 52) | 0x8000000000000, 0)
    if ax["cls"] == "inf":
        return 0x7FF0000000000000, 0
    if ax["cls"] == "zero":
        return 0xFFF0000000000000, DZ
    v = abs(ax["v"])
    n, d = v.numerator, v.denominator
    e = n.bit_length() - d.bit_length()
    if v < pow2(e):
        e -= 1
    return enc_f64_int(e), 0


def total_key(u):
    s = (u >> 15) & 1
    e = (u >> 10) & 0x1F
    f = u & 0x3FF
    if e == 0x1F and f:
        isnan_s = not (f & QBIT)
        if s:
            return (0 if not isnan_s else 1, -(f & 0x3FF))
        return (8 if isnan_s else 9, f & 0x3FF)
    if e == 0x1F:
        return (2,) if s else (7,)
    if e == 0 and f == 0:
        return (4,) if s else (5,)
    ax = dec(u)
    return (3, ax["v"]) if s else (6, ax["v"])


def op_total_order(a, b):
    ka, kb = total_key(a), total_key(b)
    return (1 if ka <= kb else 0), None


def op_total_order_mag(a, b):
    return op_total_order(a & 0x7FFF, b & 0x7FFF)


def cmp_rel(a, b):
    ax, ay = dec(a), dec(b)
    an = is_nan_d(ax["enc"])
    bn = is_nan_d(ay["enc"])
    if an or bn:
        return None
    if ax["v"] < ay["v"]:
        return -1
    if ax["v"] > ay["v"]:
        return 1
    return 0


def op_compare(pred, a, b):
    ax, ay = dec(a), dec(b)
    an, bn = is_nan_d(ax["enc"]), is_nan_d(ay["enc"])
    asn = is_snan_d(ax["enc"])
    bsn = is_snan_d(ay["enc"])
    signaling = pred.startswith("signaling")
    if an or bn:
        if signaling or asn or bsn:
            return 0, NV
        base = pred.split("_", 1)[1]
        if base in ("not_equal",):
            return 1, 0
        return 0, 0
    r = cmp_rel(a, b)
    base = pred.split("_", 1)[1]
    if base == "equal":
        return (1 if r == 0 else 0), 0
    if base == "not_equal":
        return (1 if r != 0 else 0), 0
    if base == "less":
        return (1 if r == -1 else 0), 0
    if base == "less_equal":
        return (1 if r in (-1, 0) else 0), 0
    if base == "greater":
        return (1 if r == 1 else 0), 0
    if base == "greater_equal":
        return (1 if r in (1, 0) else 0), 0
    raise ValueError(pred)
