#!/usr/bin/env python3
"""vw_ref.py - verifier-w3str INDEPENDENT exact reference (fresh code).

No imports from tests/gen_vectors_str.py. Exact rational arithmetic via
Fraction; integer IEEE round-and-pack mirror of the landed kernel
(msf_roundpack.c: unbounded tininess after rounding, Clause 7.5);
my own longest-prefix grammar parser encoding the RULED behaviors
(lead.md 2026-10-27 08:30:16: R1 no whitespace skip, R2 snan signaling
no-invalid no-suffix lowercase output, R3 mandatory p, R4 beyond-H
two-step inexact-only corner, R5 spec freeze). Bug-compatible with the
rulings, NOT with the copy under test.
"""
import sys
from fractions import Fraction

FMTS = {
    "f16": {"p": 11, "emax": 15, "emin": -14, "bias": 15, "signbit": 15},
    "f32": {"p": 24, "emax": 127, "emin": -126, "bias": 127, "signbit": 31},
    "f64": {"p": 53, "emax": 1023, "emin": -1022, "bias": 1023, "signbit": 63},
}
PMIN = {"f16": 5, "f32": 9, "f64": 17}
RMS = ("te", "tz", "tp", "tn")
FL_INEXACT = 0x10
FL_UNDERFLOW = 0x08
FL_OVERFLOW = 0x04
FL_INVALID = 0x01
H = 20


def round_inc_mag(rm, sign, cand_odd, guard, rest_nonzero):
    """Magnitude increment decision. cand_odd: lsb of kept candidate."""
    if rm == "te":
        return guard and (rest_nonzero or cand_odd)
    if rm == "tp":
        return (not sign) and (guard or rest_nonzero)
    if rm == "tn":
        return sign and (guard or rest_nonzero)
    return False  # tz


def pack(fmt, sign, v, rm):
    """v: Fraction >= 0 exact magnitude. Returns (bits_int, flags_int)."""
    fp = FMTS[fmt]
    p, emax, emin = fp["p"], fp["emax"], fp["emin"]
    if v == 0:
        return (sign << fp["signbit"]), 0
    # floor(log2(v))
    e = v.numerator.bit_length() - v.denominator.bit_length()
    if Fraction(2) ** e > v:
        e -= 1
    if Fraction(2) ** (e + 1) <= v:
        e += 1
    e_top = e
    ec = e if e >= emin else emin  # subnormal clamp
    scale = ec - p - 1
    if scale >= 0:
        tnum, tden = v.numerator, v.denominator * (1 << scale)
    else:
        tnum, tden = v.numerator * (1 << (-scale)), v.denominator
    q, r = divmod(tnum, tden)
    assert q < (1 << (p + 2)), (fmt, str(v)[:40], q.bit_length())
    cand = q >> 2
    guard = (q >> 1) & 1
    roundb = q & 1
    sticky = r != 0
    inex = guard or roundb or sticky
    if round_inc_mag(rm, sign, cand & 1, guard, roundb or sticky):
        cand += 1
    if cand >> p:
        cand >>= 1
        ec += 1
    if ec > emax:
        to_inf = (rm == "te") or (rm == "tp" and not sign) or (rm == "tn" and sign)
        if to_inf:
            # infinity: exponent all-ones, fraction zero
            if fmt == "f16":
                bits = (sign << 15) | (0x1F << 10)
            elif fmt == "f32":
                bits = (sign << 31) | (0xFF << 23)
            else:
                bits = (sign << 63) | (0x7FF << 52)
        else:
            # largest finite: emax field, all frac ones
            if fmt == "f16":
                bits = (sign << 15) | (0x1E << 10) | 0x3FF
            elif fmt == "f32":
                bits = (sign << 31) | (0xFE << 23) | 0x7FFFFF
            else:
                bits = (sign << 63) | (0x7FE << 52) | 0xFFFFFFFFFFFFF
        return bits, FL_OVERFLOW | FL_INEXACT
    flags = 0
    if inex:
        tiny = False
        if e_top < emin:
            # unbounded-rounded tininess (Clause 7.5, flags-only)
            su = e_top - p - 1
            if su >= 0:
                un, ud = v.numerator, v.denominator * (1 << su)
            else:
                un, ud = v.numerator * (1 << (-su)), v.denominator
            qu, ru = divmod(un, ud)
            cu = qu >> 2
            if round_inc_mag(rm, sign, cu & 1, (qu >> 1) & 1, (qu & 1) or (ru != 0)):
                cu += 1
            er = e_top + (1 if cu >> p else 0)
            tiny = er < emin
        flags |= FL_INEXACT
        if tiny:
            flags |= FL_UNDERFLOW
    if cand >= (1 << (p - 1)):
        bits = (sign << fp["signbit"]) | ((ec + fp["bias"]) << (p - 1)) | (cand - (1 << (p - 1)))
    else:
        bits = (sign << fp["signbit"]) | cand
    return bits, flags


def is_digit(c):
    return "0" <= c <= "9"


def parse_special(s):
    """My own longest-prefix special parser. Returns (cls, sign, consumed)
    or None. cls in inf/nan/snan."""
    i = 0
    sign = 0
    if s[:1] in ("+", "-"):
        sign = s[:1] == "-"
        i = 1
    low = s[i:].lower()
    if low.startswith("infinity"):
        return ("inf", sign, i + 8)
    if low.startswith("inf"):
        return ("inf", sign, i + 3)
    if low.startswith("snan"):
        return ("snan", sign, i + 4)
    if low.startswith("nan"):
        return ("nan", sign, i + 3)
    return None


def special_bits(fmt, cls, sign):
    fp = FMTS[fmt]
    sb = sign << fp["signbit"]
    if cls == "inf":
        if fmt == "f16":
            return sb | 0x7C00
        if fmt == "f32":
            return sb | 0x7F800000
        return sb | 0x7FF0000000000000
    if cls == "snan":
        if fmt == "f16":
            return sb | 0x7C00 | 0x0001
        if fmt == "f32":
            return sb | 0x7F800000 | 0x000001
        return sb | 0x7FF0000000000000 | 0x1
    if fmt == "f16":
        return sb | 0x7E00
    if fmt == "f32":
        return sb | 0x7FC00000
    return sb | 0x7FF8000000000000


def dec_str_round(digits, rm, sign):
    """Round a nonzero digit string to H=20 under rm on the DECIMAL string.
    Returns (kept20_str, dropped_nonzero). Exact-half ties to even on the
    last kept DECIMAL digit (correct version)."""
    assert digits and set(digits) != {"0"}
    if len(digits) <= H:
        return digits, False
    kept, tail = digits[:H], digits[H:]
    if set(tail) == {"0"}:
        return kept, False
    n = len(tail)
    tval = int(tail)
    half = 5 * (10 ** (n - 1))
    if rm == "te":
        inc = tval > half or (tval == half and (int(kept[-1]) & 1) == 1)
    elif rm == "tp":
        inc = not sign
    elif rm == "tn":
        inc = bool(sign)
    else:
        inc = False
    if inc:
        ds = [int(c) for c in kept]
        j = len(ds) - 1
        while j >= 0 and ds[j] == 9:
            ds[j] = 0
            j -= 1
        if j < 0:
            return "1" + "0" * (H - 1), True  # caller shifts exponent +1
        ds[j] += 1
        kept = "".join(str(d) for d in ds)
    return kept, True


def parse_dec_token(s):
    """Longest valid decimal finite prefix. Returns
    (D_int, e10, consumed) or None. D_int>=0, value=D*10^e10."""
    n = len(s)
    i = 0
    while i < n and s[i] in ("+", "-"):
        if i > 0:
            break
        i += 1
        break
    # only one optional sign
    j = i
    int_d = ""
    while j < n and is_digit(s[j]):
        int_d += s[j]
        j += 1
    frac_d = ""
    if j < n and s[j] == ".":
        k = j + 1
        f = ""
        while k < n and is_digit(s[k]):
            f += s[k]
            k += 1
        if int_d == "" and f == "":
            return None  # lone dot
        frac_d = f
        j = k
    elif int_d == "":
        return None
    mant = int_d + frac_d
    epos = j
    exp = 0
    hasexp = False
    if j < n and s[j] in ("e", "E"):
        k = j + 1
        es = ""
        if k < n and s[k] in ("+", "-"):
            es = s[k]
            k += 1
        d = ""
        while k < n and is_digit(s[k]):
            d += s[k]
            k += 1
        if d == "":
            pass  # incomplete exponent: not consumed
        else:
            hasexp = True
            exp = int(es + d)
            epos = k
    D = int(mant) if mant != "" else 0
    return D, exp - len(frac_d), epos


def ref_from_decimal(fmt, s, rm):
    """Independent from_decimal. Returns (bits, flags, consumed)."""
    if s == "":
        return 0, 0, 0
    sp = parse_special(s)
    if sp is not None:
        cls, sign, c = sp
        return special_bits(fmt, cls, sign), 0, c
    t = parse_dec_token(s)
    if t is None:
        return 0, 0, 0
    D, e10, c = t
    if D == 0:
        sign = s[:1] == "-"
        return (1 << FMTS[fmt]["signbit"]) if sign else 0, 0, c
    sign = s[:1] == "-"
    digits = str(D)
    if len(digits) > H:
        kept, dnz = dec_str_round(digits, rm, sign)
        carry = len(digits) - H if kept == "1" + "0" * (H - 1) and kept != digits[:H] else 0
        # renormalize: kept has H digits; value scale shifts by len(digits)-H (+1 on all-9 carry)
        D = int(kept)
        e10 = e10 + (len(digits) - H) + (1 if (kept == "1" + "0" * (H - 1) and len(digits) > H and digits[:H] == "9" * H) else 0)
        extra_inex = dnz
    else:
        extra_inex = False
    v = Fraction(D) * (Fraction(10) ** e10 if e10 >= 0 else Fraction(1, 10 ** (-e10)))
    bits, flags = pack(fmt, sign, v, rm)
    if extra_inex:
        flags |= FL_INEXACT
    return bits, flags, c


def parse_hex_token(s):
    """Longest valid hex finite prefix per 5.12.3 + mandatory p.
    Returns (H_int, nfrac, pexp, consumed) or None."""
    n = len(s)
    i = 0
    if i < n and s[i] in ("+", "-"):
        i += 1
    if not (s[i:i + 2].lower() == "0x"):
        return None
    i += 2
    int_d = ""
    while i < n and s[i].lower() in "0123456789abcdef":
        int_d += s[i]
        i += 1
    frac_d = ""
    if i < n and s[i] == ".":
        k = i + 1
        f = ""
        while k < n and s[k].lower() in "0123456789abcdef":
            f += s[k]
            k += 1
        if int_d == "" and f == "":
            return None
        frac_d = f
        i = k
    elif int_d == "":
        return None
    if i >= n or s[i] not in ("p", "P"):
        return None  # mandatory exponent (R3)
    k = i + 1
    es = ""
    if k < n and s[k] in ("+", "-"):
        es = s[k]
        k += 1
    d = ""
    while k < n and is_digit(s[k]):
        d += s[k]
        k += 1
    if d == "":
        return None
    pexp = int(es + d) if es else int(d)
    Hh = int((int_d + frac_d), 16) if (int_d + frac_d) != "" else 0
    return Hh, len(frac_d), pexp, k


def ref_from_hex(fmt, s, rm):
    if s == "":
        return 0, 0, 0
    sp = parse_special(s)
    if sp is not None:
        cls, sign, c = sp
        return special_bits(fmt, cls, sign), 0, c
    t = parse_hex_token(s)
    if t is None:
        return 0, 0, 0
    Hh, nf, pexp, c = t
    sign = s[:1] == "-"
    if Hh == 0:
        return (1 << FMTS[fmt]["signbit"]) if sign else 0, 0, c
    v = Fraction(Hh, 16 ** nf) * (Fraction(2) ** pexp if pexp >= 0 else Fraction(1, 2 ** (-pexp)))
    bits, flags = pack(fmt, sign, v, rm)
    return bits, flags, c


def decode(fmt, bits):
    """Returns dict(sign, cls, sig, exp) with cls zero/inf/qnan/snan/norm/sub."""
    fp = FMTS[fmt]
    t = fp["p"] - 1
    signbit = fp["signbit"]
    sign = (bits >> signbit) & 1
    if fmt == "f16":
        ef, fr = (bits >> 10) & 0x1F, bits & 0x3FF
        emax_biased = 0x1E
    elif fmt == "f32":
        ef, fr = (bits >> 23) & 0xFF, bits & 0x7FFFFF
        emax_biased = 0xFE
    else:
        ef, fr = (bits >> 52) & 0x7FF, bits & 0xFFFFFFFFFFFFF
        emax_biased = 0x7FE
    emaxf = emax_biased + 1  # all-ones field
    if ef == emaxf:
        if fr == 0:
            return {"sign": sign, "cls": "inf"}
        if (fr >> (t - 1)) & 1:
            return {"sign": sign, "cls": "qnan"}
        return {"sign": sign, "cls": "snan"}
    if ef == 0:
        if fr == 0:
            return {"sign": sign, "cls": "zero"}
        return {"sign": sign, "cls": "sub", "sig": fr, "exp": FMTS[fmt]["emin"] - t}
    return {"sign": sign, "cls": "norm", "sig": fr | (1 << t),
            "exp": ef - fp["bias"] - t}


def round_digit_str(digits, rm, sign):
    """Round digit string `digits` (no leading zeros, nonzero) to H digits.
    Returns (kept_str, carry_exp_bump, dropped_nonzero). Correct ties-to-even."""
    if len(digits) <= H:
        return digits, 0, False
    kept, tail = digits[:H], digits[H:]
    if set(tail) == {"0"}:
        return kept, 0, False
    n = len(tail)
    tval = int(tail)
    half = 5 * (10 ** (n - 1))
    if rm == "te":
        inc = tval > half or (tval == half and (int(kept[-1]) & 1) == 1)
    elif rm == "tp":
        inc = not sign
    elif rm == "tn":
        inc = bool(sign)
    else:
        inc = False
    if not inc:
        return kept, 0, True
    ds = [int(c) for c in kept]
    j = len(ds) - 1
    while j >= 0 and ds[j] == 9:
        ds[j] = 0
        j -= 1
    if j < 0:
        return "1" + "0" * (H - 1), 1, True
    ds[j] += 1
    return "".join(str(d) for d in ds), 0, True


def ref_to_decimal(fmt, bits, prec, style, min_d, rm):
    """Returns (out_str, length, flags). spec None -> defaults."""
    d = decode(fmt, bits)
    sign_s = "-" if d["sign"] else ""
    if d["cls"] == "inf":
        return sign_s + "inf", len(sign_s + "inf"), 0
    if d["cls"] == "qnan":
        return sign_s + "nan", len(sign_s + "nan"), 0
    if d["cls"] == "snan":
        return sign_s + "snan", len(sign_s + "snan"), 0
    if prec is None:
        prec, style, min_d = PMIN[fmt], 0, 0
    if prec <= 0:
        prec = PMIN[fmt]
    if style != 1:
        style = 0
    N = prec if (min_d is None or min_d <= 0) else max(prec, min_d)
    flags = 0
    if d["cls"] == "zero":
        dig = "0" * N
        dexp = 0
    else:
        sig, ex = d["sig"], d["exp"]
        if ex >= 0:
            big = sig << ex
            dig = str(big)
            dexp = len(dig) - 1
        else:
            big = sig * (5 ** (-ex))
            dig = str(big)
            dexp = len(dig) - 1 + ex
        assert set(dig) != {"0"}
        comp = min(N, H)
        if len(dig) > comp:
            # round first `comp` digits with tail dig[comp:]
            head, tail = dig[:comp], dig[comp:]
            kept, bump, dnz = round_head(head, tail, rm, d["sign"])
            dexp += bump
            if N > H:
                kept = kept + "0" * (N - H)
            dig = kept
            if dnz:
                flags |= FL_INEXACT
        else:
            if N > len(dig):
                dig = dig + "0" * (N - len(dig))
            else:
                dig = dig[:N] if len(dig) > N else dig
    if N == 1:
        mant = dig[0]
    else:
        mant = dig[0] + "." + dig[1:]
    if style == 0:
        es = "+" if dexp >= 0 else "-"
        ea = str(abs(dexp))
        if len(ea) < 2:
            ea = "0" + ea
        out = sign_s + mant + "e" + es + ea
    else:
        out = sign_s + fixed_place(dig, dexp)
    return out, len(out), flags


def round_head(head, tail, rm, sign):
    """Round head+tail to len(head) digits. Returns (kept, exp_bump, dnz)."""
    if tail == "" or set(tail) == {"0"}:
        return head, 0, False
    n = len(tail)
    tval = int(tail)
    half = 5 * (10 ** (n - 1))
    if rm == "te":
        inc = tval > half or (tval == half and (int(head[-1]) & 1) == 1)
    elif rm == "tp":
        inc = not sign
    elif rm == "tn":
        inc = bool(sign)
    else:
        inc = False
    if not inc:
        return head, 0, True
    ds = [int(c) for c in head]
    j = len(ds) - 1
    while j >= 0 and ds[j] == 9:
        ds[j] = 0
        j -= 1
    if j < 0:
        return "1" + "0" * (len(head) - 1), 1, True
    ds[j] += 1
    return "".join(str(x) for x in ds), 0, True


def fixed_place(dig, dexp):
    """Position N-digit significand with decimal exponent dexp, no exponent."""
    N = len(dig)
    pos = dexp + 1  # digits left of point
    if pos >= N:
        return dig + "0" * (pos - N)
    if pos <= 0:
        return "0." + "0" * (-pos) + dig
    return dig[:pos] + "." + dig[pos:]


def ref_to_hex(fmt, bits, prec, rm):
    """Returns (out_str, length, flags). prec None -> exact-enough."""
    d = decode(fmt, bits)
    sign_s = "-" if d["sign"] else ""
    t = FMTS[fmt]["p"] - 1
    if d["cls"] == "inf":
        return sign_s + "inf", len(sign_s + "inf"), 0
    if d["cls"] == "qnan":
        return sign_s + "nan", len(sign_s + "nan"), 0
    if d["cls"] == "snan":
        return sign_s + "snan", len(sign_s + "snan"), 0
    exact = prec is None or prec < 0
    if d["cls"] == "zero":
        if exact or prec == 0:
            # C %a with precision 0 emits no point: "0x0p+0"
            out = sign_s + "0x0p+0"
        else:
            out = sign_s + "0x0." + "0" * prec + "p+0"
        return out, len(out), 0
    if d["cls"] == "norm":
        sig, ue = d["sig"], d["exp"] + t  # unbiased exponent of leading 1
        # fraction in [0,1): f = sig/2^t - 1
        frem = sig - (1 << t)  # integer in [0, 2^t)
        scale = 0  # value = (1+f)*2^ue
        lead = "1"
    else:
        emin = FMTS[fmt]["emin"]
        ue = emin
        # value = sig * 2^(emin-t); fraction of 2^emin: f = sig/2^t in (0,1)
        frem = d["sig"]
        scale = 0
        lead = "0"
    # exact nibbles of frem over t bits, padded up to multiple of 4
    nb = ((t + 3) // 4)
    full = frem << (4 * nb - t)
    nibs = []
    for j in range(nb):
        nibs.append((full >> (4 * (nb - 1 - j))) & 0xF)
    flags = 0
    if exact:
        while nibs and nibs[-1] == 0:
            nibs.pop()
    else:
        P = prec
        if len(nibs) > P:
            head, tailn = nibs[:P], nibs[P:]
            # dropped value vs half ulp of last kept nibble
            # tail as integer over 4*(len-P) bits
            tv = 0
            for x in tailn:
                tv = (tv << 4) | x
            nbits = 4 * len(tailn)
            half = 1 << (nbits - 1)
            if tv == 0:
                dnz = False
                inc = False
            else:
                dnz = True
                # kept value is lead+head; tie breaks to even kept value.
                # lead "1" is odd, lead "0" is even, head empty keeps lead parity.
                parity = (head[-1] if head else int(lead)) & 1
                if rm == "te":
                    inc = tv > half or (tv == half and parity == 1)
                elif rm == "tp":
                    inc = not d["sign"]
                elif rm == "tn":
                    inc = bool(d["sign"])
                else:
                    inc = False
            if inc:
                # increment hex digit array
                j = len(head) - 1
                while j >= 0 and head[j] == 0xF:
                    head[j] = 0
                    j -= 1
                if j < 0:
                    # carry into leading digit: 1.ff..->2.00 / 0.ff..->1.00 at same exp (R5)
                    lead = "2" if lead == "1" else "1"
                    head = [0] * P
                else:
                    head[j] += 1
            nibs = head
            if dnz:
                flags |= FL_INEXACT
        else:
            nibs = nibs + [0] * (P - len(nibs))
    hexd = "".join("0123456789abcdef"[x] for x in nibs)
    if hexd == "":
        out = "%s0x%sp%+d" % (sign_s, lead, ue)
    else:
        out = "%s0x%s.%sp%+d" % (sign_s, lead, hexd, ue)
    return out, len(out), flags
