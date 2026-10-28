#!/usr/bin/env python3
"""Exact references and vectors for the character conversions (parcel-str).

Independent exact references (test code only) for the 12 wave-3
instantiations msf{16,32,64}_from_decimal / _to_decimal / _from_hex /
_to_hex. Everything is decided by integer arithmetic on Python big
integers: values are (num, den) positive integer pairs or digit
strings; no hardware arithmetic and no decimal library decides any
expectation. Semantics follow the parcel-str design entry as ruled
by the lead (R1-R6, ledger 2026-10-27 08:30:16): longest-valid-prefix
grammar with no whitespace skipping, mandatory hex p-exponent,
snan as a signaling NaN with no invalid, no NaN payload suffixes,
the 5.12.2 two-step route beyond H=20 significant decimal digits,
and the R5 output-spec freeze.

The pack reference below shares no code shape with src/msf_string.c
or the C kernel: it rounds an exact integer ratio once per Clause
4/7 with after-rounding tininess judged on the unbounded-exponent
rounding (Clause 7.5, SF-0 2.5, lead ruling 2026-10-26 22:14:34).

Provenance: committed vectors are tagged exact-str:* (this file).
Beyond-H vectors are tagged exact-str:beyond-h and must never be
described as MPFR-decided (the two-step result can differ from a
single exact rounding; lead ruling R4). MPFR cross-checks run
separately in scratch and are reported with their own counts.

Usage:
  gen_vectors_str.py directed OUTDIR          committed directed sets
  gen_vectors_str.py bulk KIND OUTFILE N SEED seeded bulk set for the
                                              scratch differential gate
  KIND is from-decimal|to-decimal|from-hex|to-hex with a
  per-destination cycle inside the file.
"""
import random
import sys
from pathlib import Path

H = 20
FMTS = {  # name: (bits, precision, exp bits, pmin)
    "f16": (16, 11, 5, 5),
    "f32": (32, 24, 8, 9),
    "f64": (64, 53, 11, 17),
}
F_INV, F_DIV0, F_OVF, F_UNF, F_INX = 0x01, 0x02, 0x04, 0x08, 0x10
RMS = ["te", "tz", "tp", "tn", "ta"]  # five attributes (SF-2 Step 1)
POW10 = {0: 1}


def pow10(n):
    v = POW10.get(n)
    if v is None:
        v = 10 ** n
        POW10[n] = v
    return v


def fmt_params(fmt):
    bits, p, w, pmin = FMTS[fmt]
    t = bits - 1 - w
    emax = (1 << (w - 1)) - 1
    return dict(bits=bits, p=p, w=w, t=t, emax=emax, emin=1 - emax,
                pmin=pmin, signbit=bits - 1)


def default_qnan(fmt):
    fp = fmt_params(fmt)
    return (((1 << fp["w"]) - 1) << fp["t"]) | (1 << (fp["t"] - 1))


def infinity(fmt, sign):
    fp = fmt_params(fmt)
    return (sign << fp["signbit"]) | (((1 << fp["w"]) - 1) << fp["t"])


# ---------------- exact pack of an integer ratio ----------------

def _floor_log2_ratio(num, den):
    """e with 2^e <= num/den < 2^(e+1), num,den > 0."""
    e = num.bit_length() - den.bit_length()
    # compare num/den with 2^e
    if e >= 0:
        if num < (den << e):
            e -= 1
    else:
        if (num << (-e)) < den:
            e -= 1
    return e


def _round_ratio_to_int(num, den, rm, sign):
    """Round num/den (>0) to an integer per rm applied to the signed
    value (-1)^sign * num/den. Returns (q, inexact)."""
    q, r = divmod(num, den)
    if r == 0:
        return q, False
    inc = False
    if rm == "te":
        twice = 2 * r
        inc = twice > den or (twice == den and (q & 1))
    elif rm == "ta":
        inc = 2 * r >= den
    elif rm == "tp":
        inc = not sign
    elif rm == "tn":
        inc = bool(sign)
    return q + (1 if inc else 0), True


def _scaled_round(num, den, scale, rm, sign):
    """Round (num/den) / 2^scale to an integer. Returns (q, inexact)."""
    if scale >= 0:
        return _round_ratio_to_int(num, den << scale, rm, sign)
    return _round_ratio_to_int(num << (-scale), den, rm, sign)


def pack_ratio(sign, num, den, rm, fmt):
    """Pack magnitude num/den into fmt. Returns (bits, flags)."""
    fp = fmt_params(fmt)
    p, t, emax, emin = fp["p"], fp["t"], fp["emax"], fp["emin"]
    if num == 0:
        return sign << fp["signbit"], 0
    e = _floor_log2_ratio(num, den)
    scale = max(e, emin) - (p - 1)
    q, inexact = _scaled_round(num, den, scale, rm, sign)
    if q == (1 << p):
        q >>= 1
        scale += 1
    # delivered magnitude = q * 2^scale; overflow iff > max finite
    maxq = (1 << p) - 1
    if scale > emax - (p - 1) or (scale == emax - (p - 1) and q > maxq):
        to_inf = rm in ("te", "ta") or (rm == "tp" and not sign) or (rm == "tn" and sign)
        expmax = (1 << fp["w"]) - 1
        enc = (expmax << t) if to_inf else (((expmax - 1) << t) | ((1 << t) - 1))
        return (sign << fp["signbit"]) | enc, F_OVF | F_INX
    flags = 0
    if inexact:
        flags |= F_INX
        if e < emin:
            scale_u = e - (p - 1)
            q_u, _ = _scaled_round(num, den, scale_u, rm, sign)
            if q_u == (1 << p):
                q_u >>= 1
                scale_u += 1
            # tiny-after iff q_u * 2^scale_u < 2^emin
            lhs = q_u
            rhs_exp = emin - scale_u
            tiny = (lhs < (1 << rhs_exp)) if rhs_exp >= 0 else True
            if rhs_exp < 0:
                tiny = (lhs << (-rhs_exp)) < 1
            if tiny:
                flags |= F_UNF
    if q >= (1 << (p - 1)):
        efield = scale + (p - 1) + emax
        return (sign << fp["signbit"]) | (efield << t) | (q - (1 << (p - 1))), flags
    return (sign << fp["signbit"]) | q, flags


def decode(fmt, x):
    fp = fmt_params(fmt)
    sign = (x >> fp["signbit"]) & 1
    efield = (x >> fp["t"]) & ((1 << fp["w"]) - 1)
    frac = x & ((1 << fp["t"]) - 1)
    if efield == (1 << fp["w"]) - 1:
        cls = "inf" if frac == 0 else ("qnan" if frac >> (fp["t"] - 1) else "snan")
        return dict(sign=sign, cls=cls, sig=frac, exp=0, frac=frac, efield=efield)
    if efield == 0:
        return dict(sign=sign, cls="zero" if frac == 0 else "sub",
                    sig=frac, exp=fp["emin"] - fp["t"], frac=frac, efield=efield)
    return dict(sign=sign, cls="norm", sig=frac | (1 << fp["t"]),
                exp=efield - fp["emax"] - fp["t"], frac=frac, efield=efield)


# ---------------- specials and shared grammar (R1/R2) ----------------

def parse_special(s, fmt):
    """Returns (bits, consumed) or None."""
    i = 0
    sign = 0
    if i < len(s) and s[i] in "+-":
        sign = 1 if s[i] == "-" else 0
        i += 1
    low = s[i:].lower()
    fp = fmt_params(fmt)
    sb = sign << fp["signbit"]
    if low.startswith("infinity"):
        return infinity(fmt, sign), i + 8
    if low.startswith("inf"):
        return infinity(fmt, sign), i + 3
    if low.startswith("snan"):
        return sb | (((1 << fp["w"]) - 1) << fp["t"]) | 1, i + 4
    if low.startswith("nan"):
        return sb | default_qnan(fmt), i + 3
    return None


def dec_round_inc(rm, sign, last_kept_digit, dropped_str):
    """Digit-string magnitude increment decision on an exact dropped
    digit tail ("5", "5001", ...). Independent integer form: compare
    the tail against half a unit of the last kept place."""
    if not dropped_str or set(dropped_str) == {"0"}:
        return False
    dropped_nonzero = True
    n = len(dropped_str)
    tail = int(dropped_str)
    half = 5 * 10 ** (n - 1)
    if rm == "te":
        return tail > half or (tail == half and (last_kept_digit & 1) == 1)
    if rm == "ta":
        return tail >= half
    if rm == "tp":
        return not sign and dropped_nonzero
    if rm == "tn":
        return bool(sign) and dropped_nonzero
    return False


def dec_increment(digits):
    """Increment a digit string; returns (new_digits, carry)."""
    ds = list(digits)
    for i in range(len(ds) - 1, -1, -1):
        if ds[i] != "9":
            ds[i] = chr(ord(ds[i]) + 1)
            return "".join(ds), False
        ds[i] = "0"
    return "1" + "0" * (len(ds) - 1), True


def clamp_exp(v, limit=100001):
    return max(-limit, min(limit, v))


# ---------------- from_decimal reference ----------------

def _pack_synth(sign, kind, rm, fmt):
    """Certain-outcome delivery for magnitudes beyond +-400 decimal
    orders vs the destination: value >= 10^400 exceeds every
    format's largest finite; value < 10^-400 is below half the
    smallest subnormal ulp of every format (2^-1075 > 10^-324).
    The pack of the named representative ratios therefore equals
    the pack of the true value in bits and flags."""
    if kind == "ovf":
        return pack_ratio(sign, 1 << 2200, 1, rm, fmt)
    return pack_ratio(sign, 1, 1 << 2200, rm, fmt)


def from_decimal_ref(s, rm, fmt):
    """Returns (bits, flags, consumed)."""
    if s is None:
        return 0, 0, 0
    sp = parse_special(s, fmt)
    if sp is not None:
        bits, c = sp
        return bits, 0, c
    fp = fmt_params(fmt)
    i = 0
    sign = 0
    if i < len(s) and s[i] in "+-":
        sign = 1 if s[i] == "-" else 0
        i += 1
    start = i
    int_digits = ""
    while i < len(s) and s[i].isdigit():
        int_digits += s[i]
        i += 1
    frac_digits = ""
    if i < len(s) and s[i] == ".":
        i += 1
        while i < len(s) and s[i].isdigit():
            frac_digits += s[i]
            i += 1
    if not int_digits and not frac_digits:
        return 0, 0, 0
    mant_end = i
    exp10 = 0
    if i < len(s) and s[i] in "eE":
        j = i + 1
        esign = 1
        if j < len(s) and s[j] in "+-":
            esign = -1 if s[j] == "-" else 1
            j += 1
        if j < len(s) and s[j].isdigit():
            v = 0
            while j < len(s) and s[j].isdigit():
                v = v * 10 + int(s[j])
                if v > 100001:
                    v = 100001
                j += 1
            exp10 = esign * v
            i = j
        else:
            i = mant_end
    del start
    all_digits = int_digits + frac_digits
    sig_str = all_digits.lstrip("0")
    if sig_str == "":
        return sign << fp["signbit"], 0, i
    e10 = exp10 - len(frac_digits)
    step1_inexact = False
    if len(sig_str) > H:
        kept = sig_str[:H]
        dropped = sig_str[H:]
        step1_inexact = set(dropped) != {"0"}
        e10 += len(sig_str) - H
        if dec_round_inc(rm, sign, int(kept[-1]), dropped):
            kept, carry = dec_increment(kept)
            if carry:
                e10 += 1
        sig_str = kept
    d = int(sig_str)
    m = len(sig_str) + e10  # value in [10^(m-1), 10^m)
    if m > 400:
        bits, flags = _pack_synth(sign, "ovf", rm, fmt)
        return bits, flags, i
    if m < -400:
        bits, flags = _pack_synth(sign, "unf", rm, fmt)
        if step1_inexact:
            flags |= F_INX
        return bits, flags, i
    if e10 >= 0:
        bits, flags = pack_ratio(sign, d * pow10(e10), 1, rm, fmt)
    else:
        bits, flags = pack_ratio(sign, d, pow10(-e10), rm, fmt)
    if step1_inexact:
        flags |= F_INX
    return bits, flags, i


# ---------------- from_hex reference ----------------

_HEXDIGITS = set("0123456789abcdefABCDEF")


def from_hex_ref(s, rm, fmt):
    """Returns (bits, flags, consumed). Strict 5.12.3 grammar."""
    if s is None:
        return 0, 0, 0
    sp = parse_special(s, fmt)
    if sp is not None:
        bits, c = sp
        return bits, 0, c
    fp = fmt_params(fmt)
    i = 0
    sign = 0
    if i < len(s) and s[i] in "+-":
        sign = 1 if s[i] == "-" else 0
        i += 1
    if not (i + 1 < len(s) and s[i] == "0" and s[i + 1] in "xX"):
        return 0, 0, 0
    i += 2
    int_part = ""
    while i < len(s) and s[i] in _HEXDIGITS:
        int_part += s[i]
        i += 1
    frac_part = ""
    if i < len(s) and s[i] == ".":
        i += 1
        while i < len(s) and s[i] in _HEXDIGITS:
            frac_part += s[i]
            i += 1
    if not int_part and not frac_part:
        return 0, 0, 0
    if not (i < len(s) and s[i] in "pP"):
        return 0, 0, 0
    j = i + 1
    esign = 1
    if j < len(s) and s[j] in "+-":
        esign = -1 if s[j] == "-" else 1
        j += 1
    if not (j < len(s) and s[j].isdigit()):
        return 0, 0, 0
    v = 0
    while j < len(s) and s[j].isdigit():
        v = v * 10 + int(s[j])
        if v > 100001:
            v = 100001
        j += 1
    i = j
    h = int(int_part + frac_part, 16) if (int_part + frac_part) else 0
    if h == 0:
        return sign << fp["signbit"], 0, i
    exp2 = esign * v - 4 * len(frac_part)
    # value = h * 2^exp2 exactly; feed pack_ratio via a shifted ratio
    # with the shift folded in halves to keep integers bounded.
    if exp2 > 4000:
        bits, flags = _pack_synth(sign, "ovf", rm, fmt)
        return bits, flags, i
    if exp2 < -4000 - h.bit_length():
        bits, flags = _pack_synth(sign, "unf", rm, fmt)
        return bits, flags, i
    if exp2 >= 0:
        bits, flags = pack_ratio(sign, h << exp2, 1, rm, fmt)
    else:
        bits, flags = pack_ratio(sign, h, 1 << (-exp2), rm, fmt)
    return bits, flags, i


# ---------------- to_decimal reference ----------------

def _exact_decimal_digits(d):
    """(digits, dexp) with value = digits[0].digits[1:] * 10^dexp,
    digits the exact finite decimal expansion (no trailing zeros
    trimmed beyond what the integer form carries)."""
    sig, exp = d["sig"], d["exp"]
    if exp >= 0:
        ds = str(sig << exp)
        return ds, len(ds) - 1
    ds = str(sig * 5 ** (-exp))
    return ds, len(ds) - 1 + exp


def _render_decimal(sign, digits, dexp, n_emit, style):
    """digits: exactly the computed significant digits (len <= H);
    emission zero-pads to n_emit."""
    digs = digits + "0" * max(0, n_emit - len(digits))
    out = "-" if sign else ""
    if style != 1:  # scientific
        out += digs[0]
        if n_emit > 1:
            out += "." + digs[1:n_emit]
        out += "e"
        out += ("-%02d" % (-dexp)) if dexp < 0 else ("+%02d" % dexp)
        return out
    point = dexp + 1
    if point <= 0:
        return out + "0." + "0" * (-point) + digs[:n_emit]
    if point >= n_emit:
        return out + digs[:n_emit] + "0" * (point - n_emit)
    return out + digs[:point] + "." + digs[point:n_emit]


def to_decimal_ref(bits, spec, rm, fmt):
    """spec = (precision, style, min_digits) or None.
    Returns (string, flags)."""
    d = decode(fmt, bits)
    if d["cls"] == "inf":
        return ("-" if d["sign"] else "") + "inf", 0
    if d["cls"] == "qnan":
        return ("-" if d["sign"] else "") + "nan", 0
    if d["cls"] == "snan":
        return ("-" if d["sign"] else "") + "snan", 0
    precision, style, min_digits = spec if spec is not None else (0, 0, 0)
    fp = fmt_params(fmt)
    n_emit = fp["pmin"] if precision <= 0 else precision
    if min_digits > n_emit:
        n_emit = min_digits
    k = min(n_emit, H)
    if d["cls"] == "zero":
        return _render_decimal(d["sign"], "0" * k, 0, n_emit, style), 0
    digits, dexp = _exact_decimal_digits(d)
    flags = 0
    if len(digits) > k:
        dropped = digits[k:]
        if set(dropped) != {"0"}:
            flags |= F_INX
        kept = digits[:k]
        if dec_round_inc(rm, d["sign"], int(kept[-1]), dropped):
            kept, carry = dec_increment(kept)
            if carry:
                dexp += 1
        digits = kept
    return _render_decimal(d["sign"], digits, dexp, n_emit, style), flags


# ---------------- to_hex reference ----------------

def to_hex_ref(bits, precision, rm, fmt):
    """precision < 0 (or None spec) = exact-enough. Returns (s, flags)."""
    d = decode(fmt, bits)
    if d["cls"] == "inf":
        return ("-" if d["sign"] else "") + "inf", 0
    if d["cls"] == "qnan":
        return ("-" if d["sign"] else "") + "nan", 0
    if d["cls"] == "snan":
        return ("-" if d["sign"] else "") + "snan", 0
    fp = fmt_params(fmt)
    t = fp["t"]
    sign_s = "-" if d["sign"] else ""
    if d["cls"] == "zero":
        if precision is None or precision < 0:
            return sign_s + "0x0p+0", 0
        frac = ("." + "0" * precision) if precision > 0 else ""
        return f"{sign_s}0x0{frac}p+0", 0
    e = (d["exp"] + t) if d["cls"] == "norm" else fp["emin"]
    lead0 = 1 if d["cls"] == "norm" else 0
    ndig = (t + 3) // 4
    exact_digits = []
    for j in range(ndig):
        shift = t - 4 * (j + 1)
        if shift >= 0:
            exact_digits.append((d["frac"] >> shift) & 0xF)
        else:
            exact_digits.append((d["frac"] << (-shift)) & 0xF)

    def fmt_exp(v):
        return ("-%d" % (-v)) if v < 0 else ("+%d" % v)

    if precision is None or precision < 0:
        digs = list(exact_digits)
        while digs and digs[-1] == 0:
            digs.pop()
        body = "%x" % lead0
        if digs:
            body += "." + "".join("%x" % v for v in digs)
        return f"{sign_s}0x{body}p{fmt_exp(e)}", 0
    shift_bits = t - 4 * precision
    if shift_bits <= 0:
        digs = exact_digits + [0] * (precision - ndig)
        body = "%x" % lead0
        if precision > 0:
            body += "." + "".join("%x" % v for v in digs[:precision])
        return f"{sign_s}0x{body}p{fmt_exp(e)}", 0
    s_val = d["sig"]
    dropped = s_val & ((1 << shift_bits) - 1)
    kept = s_val >> shift_bits
    half = 1 << (shift_bits - 1)
    inexact = dropped != 0
    inc = False
    if rm == "te":
        inc = dropped > half or (dropped == half and (kept & 1))
    elif rm == "ta":
        inc = dropped >= half
    elif rm == "tp":
        inc = not d["sign"] and inexact
    elif rm == "tn":
        inc = bool(d["sign"]) and inexact
    kept += 1 if inc else 0
    lead = kept >> (4 * precision)
    digs = [(kept >> (4 * (precision - 1 - j))) & 0xF for j in range(precision)]
    body = "%x" % lead
    if precision > 0:
        body += "." + "".join("%x" % v for v in digs)
    return f"{sign_s}0x{body}p{fmt_exp(e)}", (F_INX if inexact else 0)


# ---------------- vector line emission ----------------

def _bits_str(fmt, bits):
    return "%0*x" % (fmt_params(fmt)["bits"] // 4, bits)


def from_dec_line(s, rm, fmt, prov):
    bits, flags, c = from_decimal_ref(s, rm, fmt)
    tok = s if s != "" else "~"
    return (f"msf{fmt[1:]}_from_decimal {rm} IN={tok} -> "
            f"{_bits_str(fmt, bits)} {flags:02x} C={c} {prov}")


def from_hex_line(s, rm, fmt, prov):
    bits, flags, c = from_hex_ref(s, rm, fmt)
    tok = s if s != "" else "~"
    return (f"msf{fmt[1:]}_from_hex {rm} IN={tok} -> "
            f"{_bits_str(fmt, bits)} {flags:02x} C={c} {prov}")


def to_dec_line(bits, spec, rm, fmt, prov, buf=None):
    s, flags = to_decimal_ref(bits, spec, rm, fmt)
    spec_s = "%d,%d,%d" % spec
    mid = f"BUF={buf} " if buf is not None else ""
    out = s
    if buf is not None and len(s) + 1 > buf:
        out = "~"
    return (f"msf{fmt[1:]}_to_decimal {rm} A={_bits_str(fmt, bits)} "
            f"SPEC={spec_s} {mid}-> OUT={out} LEN={len(s)} {flags:02x} {prov}")


def to_hex_line(bits, precision, rm, fmt, prov, buf=None):
    s, flags = to_hex_ref(bits, precision, rm, fmt)
    mid = f"BUF={buf} " if buf is not None else ""
    out = s
    if buf is not None and len(s) + 1 > buf:
        out = "~"
    return (f"msf{fmt[1:]}_to_hex {rm} A={_bits_str(fmt, bits)} "
            f"SPEC={precision} {mid}-> OUT={out} LEN={len(s)} {flags:02x} {prov}")


# ---------------- directed sets ----------------

GRAMMAR_DEC = [
    "", "+", "-", ".", "+.", "-.", "e5", "E", "1e", "1e+", "1e-", "1e+x",
    "1e5x", "1.2.3", "..5", ".e5", "0", "-0", "+0", "0.0", "-0.00e10",
    "0e999999999", "-0e-999999999", "007", "0.5", ".5", "5.", "5.e2",
    ".5e-2", "1e5", "1E5", "1e+5", "1e-5", "1e005", "12.34e56",
    "0.000001", "1000000", "1e20", "1e-20", "9e99", "1e309", "1e-309",
    "1e400", "1e-400", "1e999999999", "1e-999999999", "5e-324", "2.5e-324",
    "1.7976931348623157e308", "1.7976931348623159e308", "2.2250738585072014e-308",
    "3.4028235e38", "3.4028237e38", "1.17549435e-38", "1.401298464e-45",
    "65504", "65520", "65536", "6.103515625e-05", "5.960464477539063e-08",
    "0.1", "0.2", "0.3", "0.7", "1.1", "3.14159265358979323846",
    "2.71828182845904523536", "12345678901234567890", "123456789012345678901",
    "99999999999999999999", "999999999999999999999", "100000000000000000000",
    "1.0000000000000000001", "0.50000000000000000005", "4503599627370496.5",
    "9007199254740993", "9007199254740995", "18014398509481983",
    "0x1p1", "0x10", "1a", "a1", "1,5", "--1", "++1", "+-1",
    "1ee5", "1e5e6", "5e-", ".5.", "5..5",
    "inf", "Inf", "INF", "infinity", "Infinity", "INFINITY", "infi", "infin",
    "in", "i", "infinit", "infinityy", "infx", "+inf", "-inf", "-infinity",
    "nan", "NaN", "NAN", "+nan", "-nan", "nan(1)", "nanx", "na", "n",
    "snan", "sNaN", "SNAN", "-snan", "+SNAN", "snanx", "sna", "sn",
]

GRAMMAR_HEX = [
    "", "0x", "0X", "0xg", "0xp1", "0x.p1", "0x1", "0x1.8", "0x1p", "0x1p+",
    "0x1p-", "0x1p+x", "0x1pp1", "0x1.8p1", "0X1.8P1", "0x1p0", "0x1p-0",
    "0x1p+001", "0x.8p1", "0x1.p1", "0x1.8p+1x", "+0x1p1", "-0x1p1",
    "0x0p0", "-0x0.0p999999999", "0x00001p0", "0x1.0000000000000001p0",
    "0x1.fffffffffffffp1023", "0x1.fffffffffffff8p1023", "0x1p1024",
    "0x1p-1074", "0x1p-1075", "0x1p-1076", "0x0.0000000000001p-1022",
    "0x0.00000000000008p-1022", "0x1p999999999", "0x1p-999999999",
    "0xabcdefp10", "0xABCDEFP-10", "0x1.2.3p1", "0xx1p1", "x1p1", "1.5",
    "1p1", "0x1.5e3p2", "0x1p5e3", "0x1.921fb54442d18p1",
    "0x123456789abcdef0123456789abcdef0123456789abcdefp-100",
    "0x10000000000000000000000000000000000000000000000001p-200",
    "0xffffffffffffffffffffffffffffffffffffffffffffffffffp-200",
    "inf", "INF", "infinity", "-inf", "nan", "-nan", "snan", "-SNAN",
]


def _tie_strings(fmt):
    """Exact decimal ties with <=19 digits, plus just-above/below
    variants at one finer digit. Tie values are (2q+1) * 2^E with q
    a p-bit significand, at scales whose exact decimal form fits."""
    fp = fmt_params(fmt)
    p = fp["p"]
    out = []
    qs = [1 << (p - 1), (1 << (p - 1)) + 1, (1 << p) - 2, (1 << p) - 1,
          (1 << (p - 1)) + (1 << (p // 2))]
    scales = [0, 1, 2, 3, 10, -1, -2, -3]
    for q in qs:
        odd = 2 * q + 1
        for e2 in scales:
            if p + 1 + e2 > fp["emax"] + 1:
                continue  # keep the tie inside the finite range
            # value = odd * 2^e2 = digits with dexp
            if e2 >= 0:
                digs = str(odd << e2)
                dexp = len(digs) - 1
            else:
                digs = str(odd * 5 ** (-e2))
                dexp = len(digs) - 1 + e2
            if len(digs) > 19:
                continue
            base = f"{digs[0]}.{digs[1:]}e{dexp}" if len(digs) > 1 else f"{digs}e{dexp}"
            out.append(base)
            di = int(digs)
            above = str(di * 10 + 1)
            below = str(di * 10 - 1)
            out.append(f"{above[0]}.{above[1:]}e{dexp}")
            out.append(f"{below[0]}.{below[1:]}e{dexp}")
            out.append("-" + base)
    return out


def _midpoint_string(odd, e2):
    """Exact decimal string (scientific) of odd * 2^e2, any length."""
    if e2 >= 0:
        digs = str(odd << e2)
        dexp = len(digs) - 1
    else:
        digs = str(odd * 5 ** (-e2))
        dexp = len(digs) - 1 + e2
    if len(digs) == 1:
        return f"{digs}e{dexp:+d}" if False else f"{digs}e{dexp}"
    return f"{digs[0]}.{digs[1:]}e{dexp}"


def _interesting_bits(fmt):
    fp = fmt_params(fmt)
    bits_n, t, w = fp["bits"], fp["t"], fp["w"]
    emax_e = (1 << w) - 2
    pats = [0, 1, 3, (1 << t) - 1, (1 << t),
            (emax_e << t) | ((1 << t) - 1), (emax_e << t),
            (((1 << w) - 1) << t), (((1 << w) - 1) << t) | 1,
            (((1 << w) - 1) << t) | (1 << (t - 1)),
            (((1 << w) - 1) << t) | (1 << (t - 1)) | 0x12345 % (1 << (t - 1)),
            (fp["emax"] << t),              # 1.0 (efield=bias)
            (fp["emax"] << t) | 1,
            (fp["emax"] << t) | ((1 << t) - 1),
            ((fp["emax"] + 1) << t) | 0x15555 % (1 << t),
            ((fp["emax"] - 1) << t) | ((1 << (t - 1)) - 1),
            (1 << t) | (1 << (t - 1)), (2 << t)]
    out = []
    for v in pats:
        out.append(v)
        out.append(v | (1 << (bits_n - 1)))
    return sorted(set(out))


def _write(path, lines):
    path.write_bytes("".join(line + "\n" for line in lines).encode("utf-8"))
    return len([l for l in lines if l and not l.startswith("#")])


def gen_from_dec_beyond_h_ties():
    """Beyond-H digit ties (SF-2 Step 1, study plant shape 2):
    take an exact binary midpoint M with an even lower
    neighbour, floor its decimal expansion to H digits D
    (even last digit), and emit D followed by '50000'. The
    two-step rule keeps D under te (pack -> lower neighbour,
    since D < M) and increments to D+ulp under ta (pack ->
    upper neighbour). Kept only where the reference's
    te/ta outcomes actually differ."""
    out = []
    for fmt in FMTS:
        fp = fmt_params(fmt)
        p = fp["p"]
        qs = [1 << (p - 1), (1 << (p - 1)) + 2, (1 << p) - 2,
              (1 << (p - 1)) + (1 << (p // 2 + 1))]
        found = 0
        for big_e in (0, -7, 9, fp["emin"] + 3, fp["emin"]):
            for q in qs:
                odd = 2 * q + 1
                e2 = big_e - p
                if e2 >= 0:
                    digs = str(odd << e2)
                    dexp = len(digs) - 1
                else:
                    digs = str(odd * 5 ** (-e2))
                    dexp = len(digs) - 1 + e2
                if len(digs) <= H + 1:
                    continue
                kept = digs[:H]
                if int(kept[-1]) % 2:
                    continue
                s = kept[0] + "." + kept[1:] + "50000" + f"e{dexp}"
                if from_decimal_ref(s, "te", fmt)[:2] != \
                        from_decimal_ref(s, "ta", fmt)[:2]:
                    for rm in RMS:
                        out.append(from_dec_line(s, rm, fmt,
                                                 "exact-str:beyond-h"))
                        out.append(from_dec_line("-" + s, rm, fmt,
                                                 "exact-str:beyond-h"))
                    found += 1
        assert found, fmt
    return out


def gen_to_dec_ties():
    """to_decimal digit ties: dyadic values whose exact
    decimal expansion, cut at the emitted precision, drops
    exactly '5' followed by zeros with an even kept digit
    (study plant shape 1). Searched, then decided by the
    reference in every mode."""
    out = []
    for fmt in FMTS:
        cands = []
        for n in range(1, 13):
            for k in (1, 3, 5, 9, 15, 25, 35, 45, 65, 125):
                for e in (-2, 0, 3):
                    num, den = k, 1 << n
                    if e >= 0:
                        num <<= e
                    else:
                        den <<= -e
                    for sign in (0, 1):
                        bits, fl = pack_ratio(sign, num, den, "te", fmt)
                        if fl == 0:
                            cands.append(bits)
        found = 0
        for bits in sorted(set(cands)):
            for prec in range(1, 9):
                for style in (0, 1):
                    spec = (prec, style, 0)
                    if to_decimal_ref(bits, spec, "te", fmt) != \
                            to_decimal_ref(bits, spec, "ta", fmt):
                        for rm in RMS:
                            out.append(to_dec_line(
                                bits, spec, rm, fmt,
                                "exact-str:to-dec-modes"))
                        found += 1
        assert found, fmt
    return out


def gen_to_hex_ties():
    """to_hex half ties: significands whose dropped part at
    the emitted precision is exactly half, kept part even
    (study plant shape 1)."""
    out = []
    for fmt in FMTS:
        fp = fmt_params(fmt)
        t, p, bias = fp["t"], fp["p"], fp["emax"]
        ndig = (t + 3) // 4
        found = 0
        for pr in range(0, ndig):
            shift = t - 4 * pr
            if shift <= 0:
                continue
            kbits = p - shift
            for kept in ((1 << (kbits - 1)), (1 << (kbits - 1)) + 2,
                         (1 << kbits) - 2):
                sig = (kept << shift) | (1 << (shift - 1))
                if not (1 << t) <= sig < (1 << p):
                    continue
                for sign in (0, 1):
                    bits = (sign << fp["signbit"]) | (bias << t) | \
                        (sig - (1 << t))
                    if to_hex_ref(bits, pr, "te", fmt) != \
                            to_hex_ref(bits, pr, "ta", fmt):
                        for rm in RMS:
                            out.append(to_hex_line(
                                bits, pr, rm, fmt,
                                "exact-str:to-hex-modes"))
                        found += 1
        assert found, fmt
    return out


def gen_from_hex_ties():
    """from_hex binary ties at each format's own precision:
    value = odd * 2^(e-p) with odd a p+1-bit midpoint
    significand, even lower neighbour (SF-2 Step 1)."""
    out = []
    for fmt in FMTS:
        fp = fmt_params(fmt)
        p = fp["p"]
        found = 0
        for e in (0, -5, 7, fp["emin"] + 2):
            for q in ((1 << (p - 1)), (1 << (p - 1)) + 2, (1 << p) - 2):
                odd = 2 * q + 1
                s = f"0x{odd:x}p{e - p}"
                if from_hex_ref(s, "te", fmt)[:2] != \
                        from_hex_ref(s, "ta", fmt)[:2]:
                    for rm in RMS:
                        out.append(from_hex_line(
                            s, rm, fmt, "exact-str:from-hex-ties"))
                        out.append(from_hex_line(
                            "-" + s, rm, fmt, "exact-str:from-hex-ties"))
                    found += 1
        assert found, fmt
    return out


def directed(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    header = "# generated by tests/gen_vectors_str.py - do not edit (regenerate)"
    total = 0

    lines = [header]
    for fmt in FMTS:
        for s in GRAMMAR_DEC:
            lines.append(from_dec_line(s, "te", fmt, "exact-str:grammar-dec"))
        core = [s for s in GRAMMAR_DEC if s and (s[0].isdigit() or s[0] in "+-.")]
        for s in core:
            for rm in ["tz", "tp", "tn", "ta"]:  # te covered in the pass above
                lines.append(from_dec_line(s, rm, fmt, "exact-str:grammar-dec-modes"))
        for s in _tie_strings(fmt):
            for rm in RMS:
                lines.append(from_dec_line(s, rm, fmt, "exact-str:from-dec-ties"))
        fp = fmt_params(fmt)
        # subnormal/normal boundary exact ties with short expansions,
        # and full-length midpoint expansions (beyond-H for f32/f64)
        boundary = [
            _midpoint_string(1, fp["emin"] - fp["p"]),          # half min sub
            _midpoint_string(3, fp["emin"] - fp["p"]),
            _midpoint_string((1 << fp["p"]) - 1, fp["emin"] - fp["p"] + 1),
            _midpoint_string((1 << (fp["p"] + 1)) - 1, fp["emax"] - fp["p"]),
            _midpoint_string(1, fp["emin"] - 1),
        ]
        for s in boundary:
            sig_digits = len(s.split("e")[0].replace(".", "").lstrip("-"))
            prov = ("exact-str:from-dec-ties" if sig_digits <= H
                    else "exact-str:beyond-h")
            for rm in RMS:
                lines.append(from_dec_line(s, rm, fmt, prov))
                lines.append(from_dec_line("-" + s, rm, fmt, prov))
        # beyond-H stress: long digit strings just off 20-digit roundings
        beyond = [
            "1.00000000000000000005e0", "1.00000000000000000015e0",
            "9.99999999999999999995e0", "9.99999999999999999994e0",
            "1.23456789012345678905e10", "1.2345678901234567890500001e10",
            "5.00000000000000000005e-324", "2.470328229206232720882e-324",
            "7.41098468761869816265e-324", "1.79769313486231580793e308",
            "0.1000000000000000000055511151231257827",
            "3.14159265358979323846264338327950288",
        ]
        for s in beyond:
            for rm in RMS:
                lines.append(from_dec_line(s, rm, fmt, "exact-str:beyond-h"))
    lines += gen_from_dec_beyond_h_ties()
    total += _write(outdir / "from-decimal-str.vec", lines)

    lines = [header]
    for fmt in FMTS:
        for s in GRAMMAR_HEX:
            lines.append(from_hex_line(s, "te", fmt, "exact-str:grammar-hex"))
        for s in GRAMMAR_HEX:
            if s and ("0x" in s or "0X" in s):
                for rm in RMS:
                    lines.append(from_hex_line(s, rm, fmt,
                                               "exact-str:grammar-hex-modes"))
        fp = fmt_params(fmt)
        # hex ties: guard bit exactly at half ulp, sticky variants
        for guard_digits in range(0, 40, 7):
            zeros = "0" * guard_digits
            for tail in ["8", "8" + zeros + "1", "7" + "f" * (guard_digits + 1),
                         "80000000000000000000000000000000000000001"]:
                s = f"0x1.{zeros}{tail}p0"
                for rm in RMS:
                    lines.append(from_hex_line(s, rm, fmt, "exact-str:from-hex-ties"))
        for e2 in [fp["emin"] - fp["p"] - 1, fp["emin"] - fp["p"],
                   fp["emin"] - 1, fp["emax"], fp["emax"] + 1]:
            for hs in ["0x1p", "0x3p", "0x1.8p", "0x2.8p", "0xffp"]:
                for rm in RMS:
                    lines.append(from_hex_line(f"{hs}{e2}", rm, fmt,
                                               "exact-str:from-hex-boundary"))
    lines += gen_from_hex_ties()
    total += _write(outdir / "from-hex-str.vec", lines)

    lines = [header]
    for fmt in FMTS:
        specs = [(0, 0, 0), (1, 0, 0), (5, 0, 0), (9, 0, 0),
                 (17, 0, 0), (20, 0, 0), (25, 0, 0),
                 (5, 1, 0), (17, 1, 0), (20, 1, 0),
                 (2, 0, 5), (2, 1, 6), (0, 1, 0), (3, 2, 0), (3, -1, -4)]
        for bits in _interesting_bits(fmt):
            for spec in specs:
                lines.append(to_dec_line(bits, spec, "te", fmt,
                                         "exact-str:to-dec-directed"))
            for spec in [(3, 0, 0), (3, 1, 0)]:
                for rm in RMS:
                    lines.append(to_dec_line(bits, spec, rm, fmt,
                                             "exact-str:to-dec-modes"))
        # buffer sizing: exact-fit, one short, zero, one
        for bits in _interesting_bits(fmt)[:12]:
            s, _ = to_decimal_ref(bits, (17, 0, 0), "te", fmt)
            for buf in [0, 1, len(s), len(s) + 1, len(s) + 5]:
                lines.append(to_dec_line(bits, (17, 0, 0), "te", fmt,
                                         "exact-str:to-dec-buffer", buf=buf))
        # huge precision (length arithmetic, small buffer never fits)
        one = (fmt_params(fmt)["emax"] << fmt_params(fmt)["t"])
        lines.append(to_dec_line(one, (1000000, 0, 0), "te", fmt,
                                 "exact-str:to-dec-buffer", buf=64))
        lines.append(to_dec_line(one, (1000000, 1, 0), "te", fmt,
                                 "exact-str:to-dec-buffer", buf=64))
    lines += gen_to_dec_ties()
    total += _write(outdir / "to-decimal-str.vec", lines)

    lines = [header]
    for fmt in FMTS:
        fp = fmt_params(fmt)
        ndig = (fp["t"] + 3) // 4
        precs = [-1, 0, 1, 2, ndig - 1, ndig, ndig + 1, 30]
        for bits in _interesting_bits(fmt):
            for pr in precs:
                lines.append(to_hex_line(bits, pr, "te", fmt,
                                         "exact-str:to-hex-directed"))
            for pr in [0, ndig - 1]:
                for rm in RMS:
                    lines.append(to_hex_line(bits, pr, rm, fmt,
                                             "exact-str:to-hex-modes"))
        for bits in _interesting_bits(fmt)[:12]:
            s, _ = to_hex_ref(bits, -1, "te", fmt)
            for buf in [0, 1, len(s), len(s) + 1]:
                lines.append(to_hex_line(bits, -1, "te", fmt,
                                         "exact-str:to-hex-buffer", buf=buf))
        one = (fp["emax"] << fp["t"])
        lines.append(to_hex_line(one, 1000000, "te", fmt,
                                 "exact-str:to-hex-buffer", buf=64))
    lines += gen_to_hex_ties()
    total += _write(outdir / "to-hex-str.vec", lines)
    print(f"directed: wrote {total} vectors into {outdir}")
    return total


# ---------------- bulk seeded sets (scratch gate) ----------------

def _rand_decimal_string(rng, fmt):
    fp = fmt_params(fmt)
    style = rng.random()
    ndig = rng.randint(1, 22) if rng.random() < 0.06 else rng.randint(1, 20)
    digits = "".join(rng.choice("0123456789") for _ in range(ndig))
    if rng.random() < 0.1:
        digits = "0" * rng.randint(0, 4) + digits
    sign = rng.choice(["", "", "-", "+"])
    # decimal exponent range biased around the format's useful band
    lo = {5: -12, 9: -50, 17: -330}[fp["pmin"]]
    hi = {5: 10, 9: 45, 17: 315}[fp["pmin"]]
    dexp = rng.randint(lo, hi)
    if style < 0.45:
        s = digits[0] + ("." + digits[1:] if len(digits) > 1 else "") + f"e{dexp}"
    elif style < 0.7:
        cut = rng.randint(0, len(digits))
        s = digits[:cut] + "." + digits[cut:]
        if rng.random() < 0.5:
            s += f"E{dexp:+d}"
    else:
        s = digits + (f"e{dexp}" if rng.random() < 0.5 else "")
        if rng.random() < 0.1:
            s += rng.choice(["x", "e", "e+", ".5", " "]) .replace(" ", "q")
    return sign + s


def _rand_bits(rng, fmt):
    fp = fmt_params(fmt)
    r = rng.random()
    if r < 0.55:  # finite, mostly normal
        v = rng.getrandbits(fp["bits"]) & ~( ((1 << fp["w"]) - 1) << fp["t"])
        e = rng.randint(0, (1 << fp["w"]) - 2)
        return v | (e << fp["t"])
    if r < 0.7:   # subnormal / boundary exponents
        e = rng.choice([0, 1, 2, (1 << fp["w"]) - 3, (1 << fp["w"]) - 2])
        return (rng.getrandbits(fp["bits"] - fp["w"]) |
                (e << fp["t"]) | (rng.randint(0, 1) << fp["signbit"]))
    return rng.getrandbits(fp["bits"])


def bulk(kind, outfile, n, seed):
    rng = random.Random(seed)
    fmts = list(FMTS)
    lines = [f"# bulk {kind} seed={seed} - scratch differential set"]
    for i in range(n):
        fmt = fmts[i % 3]
        rm = RMS[rng.randint(0, len(RMS) - 1)]
        if kind == "from-decimal":
            lines.append(from_dec_line(_rand_decimal_string(rng, fmt), rm,
                                       fmt, "exact-str:bulk-from-dec"))
        elif kind == "to-decimal":
            spec = (rng.choice([-1, 0, 1, 2, 3, 5, 9, 17, 20, 21, 30]),
                    rng.choice([0, 0, 1]),
                    rng.choice([0, 0, 0, 1, 4, 8, 25]))
            lines.append(to_dec_line(_rand_bits(rng, fmt), spec, rm, fmt,
                                     "exact-str:bulk-to-dec"))
        elif kind == "from-hex":
            nd = rng.randint(1, 40)
            digs = "".join(rng.choice("0123456789abcdef") for _ in range(nd))
            cut = rng.randint(0, nd)
            sig = digs[:cut] + ("." + digs[cut:] if rng.random() < 0.7 else digs[cut:])
            fp = fmt_params(fmt)
            p = rng.randint(fp["emin"] - fp["p"] - 60, fp["emax"] + 60)
            s = rng.choice(["", "-", "+"]) + rng.choice(["0x", "0X"]) + sig + f"p{p}"
            lines.append(from_hex_line(s, rm, fmt, "exact-str:bulk-from-hex"))
        elif kind == "to-hex":
            pr = rng.choice([-1, -1, 0, 1, 2, 3, 6, 13, 14, 20, 40])
            lines.append(to_hex_line(_rand_bits(rng, fmt), pr, rm, fmt,
                                     "exact-str:bulk-to-hex"))
        else:
            raise SystemExit(f"unknown bulk kind {kind}")
    Path(outfile).write_bytes("".join(l + "\n" for l in lines).encode("utf-8"))
    print(f"bulk {kind}: wrote {n} vectors seed={seed} -> {outfile}")


def f16_exhaustive(outfile):
    """Every binary16 encoding to_decimal at several specs and to_hex
    exact + precision variants (bulk scratch gate)."""
    lines = ["# f16 exhaustive char output - scratch gate"]
    specs = [(1, 0, 0), (5, 0, 0), (17, 0, 0), (20, 0, 0), (5, 1, 0), (17, 1, 0)]
    for bits in range(65536):
        for spec in specs:
            lines.append(to_dec_line(bits, spec, "te", "f16",
                                     "exact-str:f16-exhaustive-dec"))
        for pr in [-1, 0, 3, 5]:
            lines.append(to_hex_line(bits, pr, "te", "f16",
                                     "exact-str:f16-exhaustive-hex"))
    Path(outfile).write_bytes("".join(l + "\n" for l in lines).encode("utf-8"))
    print(f"f16-exhaustive: wrote {len(lines) - 1} vectors -> {outfile}")


def main(argv):
    if len(argv) >= 3 and argv[1] == "directed":
        directed(argv[2])
        return 0
    if len(argv) >= 6 and argv[1] == "bulk":
        bulk(argv[2], argv[3], int(argv[4]), int(argv[5]))
        return 0
    if len(argv) >= 3 and argv[1] == "f16-exhaustive":
        f16_exhaustive(argv[2])
        return 0
    sys.stderr.write(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))




