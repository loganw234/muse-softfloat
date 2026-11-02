#!/usr/bin/env python3
"""verifier-w5aug's OWN exact reference for Clause 9.5 augmented arithmetic.

Written fresh from the S1 clause extracts (scratch/S1/extract/p069.txt,
p070.txt) and the ratified flag table in ledger/parcel-w5aug.md (P1=R2).
Not ported from tests/gen_vectors_aug.py; different code shape (integer
grid arithmetic over decoded (sign, mag, exp) triples instead of
Fraction neighbour logic). Cross-checked against the extracts, not
against the copy's kernel or generator.

Rule implemented (default handling only):
  head = RTTZ(exact); ties keep the smaller magnitude, never ties-to-even.
  overflow: |exact| strictly above maxfin+half-ulp -> inf+O+I; equal ->
    max-finite.  (p069 L13-16)
  residual r = exact - head (exact integer arithmetic).
  r == 0            -> tail = zero with head's sign, no flags. (p069 L23-24)
  add/sub, r != 0   -> tail = r exactly (always representable: asserted,
                       never assumed), no flags even if tiny (P1=R2: 9.5
                       "signaled" + 7.5 exact branch; p069 L31-33).
  mul, r != 0, representable -> tail = r exactly, no flags.
  mul, r != 0, unrepresentable (a nonzero digit strictly between
    +-b^(emin-p+1), p070 L17-19) -> tail = RTTZ(r) (zero keeps r's sign),
    underflow+inexact. (p070 L21)
  NaN: first signaling (quieted, invalid) else first quiet (no flag);
    invalid with no NaN in -> default qNaN + invalid. (6.2.3 matrix,
    project order; both outputs identical)
  inf: exact infinity from an inf operand -> twice, no flag; inf-inf
    opposite (add/sub) and 0*inf (mul) -> invalid, default qNaN twice.
  exact zero: mul -> XOR sign; add/sub both-zero -> common effective
    sign else +0; cancellation/nonzero-rounding-to-zero takes the exact
    sign (RTTZ never heads toward -inf, so cancellation is +0).

Public entry: ref(fmt, op, a, b) -> (head_bits, tail_bits, flags).
fmt in ("f16","f32","f64"); op in ("add","sub","mul").
"""
import sys

FMTS = {
    "f16": {"bits": 16, "p": 11, "emax": 15, "emin": -14},
    "f32": {"bits": 32, "p": 24, "emax": 127, "emin": -126},
    "f64": {"bits": 64, "p": 53, "emax": 1023, "emin": -1022},
}
INVALID, DIVZ, OVERFLOW, UNDERFLOW, INEXACT = 0x01, 0x02, 0x04, 0x08, 0x10


def _q(fmt):
    d = FMTS[fmt]
    bits, p, emax = d["bits"], d["p"], d["emax"]
    t = p - 1
    return {
        "bits": bits, "p": p, "t": t, "emax": emax, "emin": d["emin"],
        "sign": 1 << (bits - 1),
        "expmax": (1 << (bits - 1 - t)) - 1,
        "fracmask": (1 << t) - 1,
        "inf": ((1 << (bits - 1 - t)) - 1) << t,
        "qbit": 1 << (t - 1),
        "u0exp": d["emin"] - t,  # subnormal step exponent
    }


def decode(fmt, x):
    """-> (cls, sign, mag, exp); value = (-1)^sign * mag * 2^exp."""
    q = _q(fmt)
    sign = (x >> (q["bits"] - 1)) & 1
    e = (x >> q["t"]) & q["expmax"]
    f = x & q["fracmask"]
    if e == q["expmax"]:
        if f == 0:
            return ("inf", sign, 0, 0)
        return ("snan" if (f & q["qbit"]) == 0 else "qnan", sign, f, 0)
    if e == 0:
        if f == 0:
            return ("zero", sign, 0, q["u0exp"])
        return ("finite", sign, f, q["u0exp"])
    return ("finite", sign, (1 << q["t"]) | f, e - (q["expmax"] >> 1) - q["t"])


def default_qnan(fmt):
    q = _q(fmt)
    return q["inf"] | q["qbit"]


def encode(fmt, sign, mag, exp):
    """Bits of (-1)^sign*mag*2^exp, or None if unrepresentable."""
    q = _q(fmt)
    if mag == 0:
        return q["sign"] if sign else 0
    if mag < 0:
        raise AssertionError("negative mag")
    top = exp + mag.bit_length() - 1
    if top > q["emax"]:
        return None
    step = top - q["p"] + 1
    if step < q["u0exp"]:
        step = q["u0exp"]
    sh = step - exp
    if sh > 0:
        if mag & ((1 << sh) - 1):
            return None
        m = mag >> sh
    else:
        m = mag << (-sh)
    if m.bit_length() > q["p"]:
        return None
    sb = q["sign"] if sign else 0
    if m < (1 << (q["p"] - 1)):
        return (sb | m) if step == q["u0exp"] else None
    # normal: m has p bits, top bit implicit
    return sb | ((top + (q["expmax"] >> 1)) << q["t"]) | (m - (1 << q["t"]))


def grid_rttz(fmt, sign, mag, exp):
    """RTTZ round of nonzero (sign,mag,exp). Returns (bits, None) with
    bits=None meaning overflow (caller delivers signed inf). Zero
    results (tiny rounding to zero) keep the incoming sign. Exact ties
    keep the smaller magnitude: increment only strictly above half."""
    q = _q(fmt)
    assert mag > 0
    maxfin_mag = (1 << q["p"]) - 1
    maxfin_exp = q["emax"] - q["t"]
    # overflow threshold: maxfin + half ulp above maxfin
    thr_mag = maxfin_mag * 2 + 1  # (2^(p+1)-1) at scale maxfin_exp-1
    thr_exp = maxfin_exp - 1
    if _cmp(mag, exp, thr_mag, thr_exp) > 0:
        return None, True
    top = exp + mag.bit_length() - 1
    # subnormal-clamped grid step at this binade
    step = top - q["p"] + 1
    if step < q["u0exp"]:
        step = q["u0exp"]
    # renormalize landing on 2^p (carry into next binade)
    sh = step - exp
    if sh <= 0:
        m = mag << (-sh)
        return encode(fmt, sign, m, step), False
    quo = mag >> sh
    rem = mag - (quo << sh)
    half = 1 << (sh - 1)
    if rem > half:
        quo += 1
    # rem == half (exact tie): keep quo = smaller magnitude. Never +1.
    if quo.bit_length() > q["p"]:
        # carried into the next binade; re-place at the coarser step
        quo >>= 1
        step += 1
        top += 1
        if top > q["emax"]:
            return None, True
    return encode(fmt, sign, quo, step), False


def _cmp(mag1, exp1, mag2, exp2):
    e = exp1 if exp1 < exp2 else exp2
    v1, v2 = mag1 << (exp1 - e), mag2 << (exp2 - e)
    return (v1 > v2) - (v1 < v2)


def ref(fmt, op, a, b):
    q = _q(fmt)
    ca, sa, ma, ea = decode(fmt, a)
    cb, sb, mb, eb = decode(fmt, b)
    # NaN matrix: (b) first signaling quieted + invalid; (c) first quiet.
    for cls, bits in ((ca, a), (cb, b)):
        if cls == "snan":
            nb = bits | q["qbit"]
            return nb, nb, INVALID
    for cls, bits in ((ca, a), (cb, b)):
        if cls == "qnan":
            return bits, bits, 0
    eff_b = sb ^ (1 if op == "sub" else 0)
    if op == "mul":
        bad = (ca == "zero" and cb == "inf") or (ca == "inf" and cb == "zero")
    else:
        bad = ca == "inf" and cb == "inf" and sa != eff_b
    if bad:
        dn = default_qnan(fmt)
        return dn, dn, INVALID
    if ca == "inf" or cb == "inf":
        s = (sa ^ sb) if op == "mul" else (sa if ca == "inf" else eff_b)
        ib = (q["sign"] if s else 0) | q["inf"]
        return ib, ib, 0
    # exact value as (sign, mag, exp)
    if op == "mul":
        esign, emag, eexp = sa ^ sb, ma * mb, ea + eb
    else:
        e0 = ea if ea < eb else eb
        av, bv = ma << (ea - e0), mb << (eb - e0)
        eexp = e0
        if sa == eff_b:
            esign, emag = sa, av + bv
        elif av >= bv:
            esign, emag = sa, av - bv
        else:
            esign, emag = eff_b, bv - av
    if emag == 0:
        if op == "mul":
            zs = sa ^ sb
        elif ca == "zero" and cb == "zero":
            zs = sa if sa == eff_b else 0
        else:
            # exact cancellation with nonzero operands: opposite
            # effective signs -> +0 (RTTZ never heads toward -inf).
            zs = 0
        zb = q["sign"] if zs else 0
        return zb, zb, 0
    hbits, ovf = grid_rttz(fmt, esign, emag, eexp)
    if ovf or hbits is None:
        ib = (q["sign"] if esign else 0) | q["inf"]
        return ib, ib, OVERFLOW | INEXACT
    # residual r = exact - head, at the coarser scale
    hv = _val_of(fmt, hbits)
    assert hv is not None
    hs, hmag, hexp = hv
    e0 = eexp if eexp < hexp else hexp
    ev, hvv = emag << (eexp - e0), hmag << (hexp - e0)
    # head keeps the exact sign (grid_rttz preserves it), so the
    # residual is a same-scale magnitude difference.
    assert esign == hs
    rmag = ev - hvv if ev >= hvv else hvv - ev
    rsign = esign if ev >= hvv else esign ^ 1
    if rmag == 0:
        hsbit = (hbits >> (q["bits"] - 1)) & 1
        return hbits, (q["sign"] if hsbit else 0), 0
    tbits = encode(fmt, rsign, rmag, e0)
    if tbits is not None:
        # representable residual incl. tiny-exact: NO flag (P1=R2).
        return hbits, tbits, 0
    if op != "mul":
        raise AssertionError(
            "add/sub residual unrepresentable: %s %s %04x %04x" % (fmt, op, a, b))
    # the one inexact cell: tail = RTTZ(r), underflow+inexact.
    tb, tov = grid_rttz(fmt, rsign, rmag, e0)
    assert not tov and tb is not None
    return hbits, tb, UNDERFLOW | INEXACT


def _val_of(fmt, bits):
    """(sign, mag, exp) of a finite/zero encoding, None for non-finite."""
    cls, sign, mag, exp = decode(fmt, bits)
    if cls in ("zero", "finite"):
        return sign, mag, exp
    return None


def fmt_hex(fmt, x):
    w = {"f16": 4, "f32": 8, "f64": 16}[fmt]
    return "%0*x" % (w, x)


if __name__ == "__main__":
    # smoke: tie discriminator at f16: 1.0 + ulp/2 -> tie, smaller mag.
    h, t, f = ref("f16", "add", 0x3c00, 0x1400)
    print("1+ulp/2:", fmt_hex("f16", h), fmt_hex("f16", t), "%02x" % f)
