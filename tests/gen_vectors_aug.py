#!/usr/bin/env python3
"""Committed vectors for Clause 9.5 augmented arithmetic.

Project-exact authority (operations.tsv: project-exact).
The deciding reference below computes with exact Fractions
throughout: operands decode to dyadic rationals, the exact
result is a Fraction, the head is that Fraction rounded on
the format grid by roundTiesTowardZero, the tail is the
Fraction residual (or its own grid rounding in the one
unrepresentable mul cell). That is a different code shape
from the C kernel (u128 windows plus a bits-only pack), and
every emitted case additionally passes the independent
neighbour checker `check_pair`, which re-decides the head
and tail from predecessor/successor distances and the
flags from a separately written restatement of the
ratified table; generation refuses on any disagreement.

The flag table decided here is the parcel entry gate's
second read (ledger/parcel-w5aug.md), default handling:

  signaling NaN in     -> invalid        (qNaN bits twice)
  quiet NaN in only    -> none           (qNaN bits twice)
  invalid, no NaN in   -> invalid        (default qNaN x2)
  exact inf from inf   -> none           (inf twice)
  finite head overflow -> overflow+inexact (inf twice)
  residual 0           -> none
  residual exact, any  -> none  (P1 = R2: an exact tiny
    size, incl. tiny        residual signals underflow
                            but raises no flag, 7.5)
  mul residual not     -> underflow+inexact
    representable
  divisionByZero       -> never

NaN bit choice is the SF-0 2.5 matrix restricted to one
format (first signaling operand quieted, else first quiet
NaN, else the default quiet NaN), delivered twice.

Families (counts printed at generation): specials
(NaN/inf/zero matrix in both operand orders), pool cross
product, RTTZ tie discriminators (add/sub constructed,
mul found by exact midpoint search), overflow-threshold
tie and one step each side (add direct; mul tie by the
2^(p+1)-1 factorisation), huge-gap verbatim pairs,
zero-sign cells, tiny-exact-residual (P1) cells by exact
search, mul below-step cells (including tail-to-zero and
tail-to-min-normal), seeded sweeps. Directed lines carry
exact-py-t2:augmented-directed, seeded lines
exact-py-t2:augmented-seeded.

Usage: gen_vectors_aug.py OUTDIR  (writes aug-f16.vec,
aug-f32.vec, aug-f64.vec; byte-identical regeneration)
"""
import random
import sys
from fractions import Fraction
from pathlib import Path

FMTS = {"f16": (16, 5), "f32": (32, 8), "f64": (64, 11)}
INVALID, OVERFLOW, UNDERFLOW, INEXACT = 0x01, 0x04, 0x08, 0x10
PROV_D = "exact-py-t2:augmented-directed"
PROV_S = "exact-py-t2:augmented-seeded"
OPS = ("add", "sub", "mul")


def params(fmt):
    bits, w = FMTS[fmt]
    t = bits - 1 - w
    bias = (1 << (w - 1)) - 1
    return {
        "bits": bits, "w": w, "t": t, "p": t + 1, "bias": bias,
        "emin": 1 - bias, "emax": bias, "emaxf": (1 << w) - 1,
        "sign": 1 << (bits - 1), "fracmask": (1 << t) - 1,
        "qbit": 1 << (t - 1), "inf": ((1 << w) - 1) << t,
        "qnan": (((1 << w) - 1) << t) | (1 << (t - 1)),
        "u0e": (1 - bias) - t,
    }


def classify(fmt, x):
    q = params(fmt)
    sign = (x >> (q["bits"] - 1)) & 1
    e = (x >> q["t"]) & q["emaxf"]
    f = x & q["fracmask"]
    if e == q["emaxf"]:
        cls = "inf" if f == 0 else ("qnan" if f & q["qbit"] else "snan")
    elif e == 0:
        cls = "zero" if f == 0 else "finite"
    else:
        cls = "finite"
    return cls, sign, e, f


def value_of(fmt, x):
    """Exact Fraction of a finite encoding."""
    q = params(fmt)
    cls, sign, e, f = classify(fmt, x)
    assert cls in ("zero", "finite")
    if e == 0:
        mag, exp = f, q["u0e"]
    else:
        mag, exp = (1 << q["t"]) | f, e - q["bias"] - q["t"]
    v = Fraction(mag) * Fraction(2) ** exp
    return -v if sign else v


def encode_exact(fmt, sign, mag, exp):
    """Bits of (-1)^sign * mag * 2^exp (mag >= 0 int) or None."""
    q = params(fmt)
    if mag == 0:
        return q["sign"] if sign else 0
    top = exp + mag.bit_length() - 1
    if top > q["emax"]:
        return None
    step = max(top - q["p"] + 1, q["u0e"])
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
        return sb | m if step == q["u0e"] else None
    bl = m.bit_length()
    sig = m << (q["p"] - bl)
    return sb | ((top + q["bias"]) << q["t"]) | (sig - (1 << q["t"]))


def encode_fraction(fmt, v):
    """Bits of an exact Fraction, or None if unrepresentable."""
    if v == 0:
        return None  # caller owns the zero sign
    sign = 1 if v < 0 else 0
    a = abs(v)
    num, den = a.numerator, a.denominator
    if den & (den - 1):
        return None
    return encode_exact(fmt, sign, num, -(den.bit_length() - 1))


def floor_log2_frac(a):
    """floor(log2(a)) for a positive Fraction, exactly."""
    e = a.numerator.bit_length() - a.denominator.bit_length()
    if Fraction(2) ** e > a:
        e -= 1
    assert Fraction(2) ** e <= a < Fraction(2) ** (e + 1)
    return e


def rttz(fmt, v):
    """Round a nonzero Fraction by roundTiesTowardZero.
    Returns (bits, value) with bits=None on overflow."""
    q = params(fmt)
    sign = 1 if v < 0 else 0
    a = abs(v)
    maxfin = Fraction((1 << q["p"]) - 1) * Fraction(2) ** (q["emax"] - q["t"])
    thresh = maxfin + Fraction(2) ** (q["emax"] - q["t"] - 1)
    if a > thresh:
        return None, None
    e = floor_log2_frac(a)
    step_e = max(e - q["p"] + 1, q["u0e"])
    scaled = a / Fraction(2) ** step_e
    whole = scaled.numerator // scaled.denominator
    rem = scaled - whole
    if rem > Fraction(1, 2):  # exact half stays: ties toward zero
        whole += 1
    bits = encode_exact(fmt, sign, whole, step_e)
    assert bits is not None, (fmt, v)
    val = Fraction(whole) * Fraction(2) ** step_e
    return bits, (-val if sign else val)


def ref_augmented(fmt, a, b, op):
    """The deciding reference. Returns (head, tail, flags,
    info) where info carries the classification used by the
    family searches and the independent checker."""
    q = params(fmt)
    ca, cb = classify(fmt, a), classify(fmt, b)
    info = {"kind": None, "exact": None, "resid": None,
            "r_tiny": False, "r_repr": True, "tie": False}
    # SF-0 2.5 matrix, same format: (b) first signaling,
    # quieted; else (c) first quiet; else (a) default.
    for bits, (cls, _s, _e, _f) in ((a, ca), (b, cb)):
        if cls == "snan":
            nb = bits | q["qbit"]
            info["kind"] = "snan"
            return nb, nb, INVALID, info
    for bits, (cls, _s, _e, _f) in ((a, ca), (b, cb)):
        if cls == "qnan":
            info["kind"] = "qnan"
            return bits, bits, 0, info
    sa, sb = ca[1], cb[1]
    eff_b = sb ^ (1 if op == "sub" else 0)
    if op == "mul":
        invalid = (ca[0] == "zero" and cb[0] == "inf") or (
            ca[0] == "inf" and cb[0] == "zero")
    else:
        invalid = ca[0] == "inf" and cb[0] == "inf" and sa != eff_b
    if invalid:
        info["kind"] = "invalid"
        return q["qnan"], q["qnan"], INVALID, info
    if ca[0] == "inf" or cb[0] == "inf":
        s = (sa ^ sb) if op == "mul" else (sa if ca[0] == "inf" else eff_b)
        ib = (q["sign"] if s else 0) | q["inf"]
        info["kind"] = "inf-exact"
        return ib, ib, 0, info
    va, vb = value_of(fmt, a), value_of(fmt, b)
    exact = va + vb if op == "add" else va - vb if op == "sub" else va * vb
    info["exact"] = exact
    if exact == 0:
        if op == "mul":
            s = sa ^ sb
        elif ca[0] == "zero" and cb[0] == "zero":
            s = sa if sa == eff_b else 0
        else:
            s = 0  # cancellation: +0 (RTTZ is not toward -inf)
        zb = q["sign"] if s else 0
        info["kind"] = "exact-zero"
        return zb, zb, 0, info
    hbits, hval = rttz(fmt, exact)
    if hbits is None:
        s = 1 if exact < 0 else 0
        ib = (q["sign"] if s else 0) | q["inf"]
        info["kind"] = "overflow"
        return ib, ib, OVERFLOW | INEXACT, info
    r = exact - hval
    info["resid"] = r
    hs = (hbits >> (q["bits"] - 1)) & 1
    if r == 0:
        info["kind"] = "exact"
        return hbits, (q["sign"] if hs else 0), 0, info
    info["r_tiny"] = abs(r) < Fraction(2) ** q["emin"]
    tbits = encode_fraction(fmt, r)
    if tbits is None:
        assert op == "mul", ("add/sub residual unrepresentable", fmt, a, b)
        info["r_repr"] = False
        tbits, _ = rttz(fmt, r)
        assert tbits is not None
        info["kind"] = "mul-inexact-tail"
        return hbits, tbits, UNDERFLOW | INEXACT, info
    info["kind"] = "tiny-exact" if info["r_tiny"] else "pair-exact"
    return hbits, tbits, 0, info  # P1 = R2: no flag, 7.5


def magnitude_key(fmt, x):
    """Finite encodings ordered by magnitude: sign-magnitude."""
    q = params(fmt)
    return x & ~q["sign"]


def neighbour_values(fmt, bits):
    """(below, above) finite neighbour Values of a finite
    nonzero encoding, by magnitude steps; None past ends."""
    q = params(fmt)
    sign = (bits >> (q["bits"] - 1)) & 1
    mag = bits & ~q["sign"]
    sb = q["sign"] if sign else 0
    below = value_of(fmt, sb | (mag - 1)) if mag > 0 else None
    above = None
    if mag + 1 < q["inf"]:
        above = value_of(fmt, sb | (mag + 1))
    return below, above


def verify_rttz(fmt, exact, bits):
    """Head checker: bits must be the RTTZ rounding of the
    Fraction exact, decided by neighbour distances only."""
    q = params(fmt)
    cls, _s, _e, _f = classify(fmt, bits)
    if cls == "inf":
        maxfin = Fraction((1 << q["p"]) - 1) * Fraction(2) ** (q["emax"] - q["t"])
        return abs(exact) > maxfin + Fraction(2) ** (q["emax"] - q["t"] - 1)
    hv = value_of(fmt, bits)
    if hv == 0:
        u0 = Fraction(2) ** q["u0e"]
        return abs(exact) <= u0 / 2 and (
            exact == 0 or ((bits & q["sign"]) != 0) == (exact < 0))
    if (hv < 0) != (exact < 0):
        return False
    below, above = neighbour_values(fmt, bits)
    d = abs(exact - hv)
    for nb, is_above in ((below, False), (above, True)):
        if nb is None:
            continue
        dn = abs(exact - nb)
        if dn < d:
            return False
        if dn == d and d != 0:
            # tie: the smaller magnitude must be delivered
            if abs(nb) < abs(hv):
                return False
    return True


def is_tie(fmt, exact, hbits):
    """Exact value is a midpoint beside the delivered head."""
    hv = value_of(fmt, hbits)
    if hv == exact:
        return False
    below, above = neighbour_values(fmt, hbits)
    d = abs(exact - hv)
    return any(nb is not None and abs(exact - nb) == d
               for nb in (below, above))


def check_pair(fmt, a, b, op, head, tail, flags, info):
    """Independent checker: neighbour distances for bits,
    the ratified table restated for flags. Generation
    refuses (asserts) on any disagreement."""
    q = params(fmt)
    ca, cb = classify(fmt, a), classify(fmt, b)
    nan_in = ca[0] in ("qnan", "snan") or cb[0] in ("qnan", "snan")
    if nan_in:
        assert head == tail and classify(fmt, head)[0] == "qnan"
        want = INVALID if ca[0] == "snan" or cb[0] == "snan" else 0
        assert flags == want, (fmt, a, b, op, flags, want)
        return
    if info["kind"] == "invalid":
        assert head == tail == q["qnan"] and flags == INVALID
        return
    if info["kind"] in ("inf-exact", "overflow"):
        assert head == tail and classify(fmt, head)[0] == "inf"
        if info["kind"] == "overflow":
            assert classify(fmt, a)[0] != "inf"
            assert verify_rttz(fmt, info["exact"], head)
            assert flags == OVERFLOW | INEXACT
        else:
            assert flags == 0
        return
    exact = info["exact"]
    assert verify_rttz(fmt, exact, head), (fmt, a, b, op, head)
    hv = value_of(fmt, head)
    r = exact - hv
    assert r == info["resid"] if exact != 0 else True
    if exact == 0:
        assert value_of(fmt, head) == 0 and head == tail and flags == 0
        return
    if r == 0:
        assert value_of(fmt, tail) == 0
        assert (tail & q["sign"]) == (head & q["sign"])
        assert flags == 0
        return
    if encode_fraction(fmt, r) is not None:
        assert value_of(fmt, tail) == r
        assert hv + value_of(fmt, tail) == exact
        assert flags == 0  # includes the P1 tiny-exact cell
    else:
        assert op == "mul"
        assert verify_rttz(fmt, r, tail), (fmt, a, b, op, tail)
        assert flags == UNDERFLOW | INEXACT


def emit(lines, seen, fmt, a, b, op, prov):
    key = (fmt, a, b, op)
    if key in seen:
        return None
    seen.add(key)
    head, tail, flags, info = ref_augmented(fmt, a, b, op)
    check_pair(fmt, a, b, op, head, tail, flags, info)
    hx = {16: "%04x", 32: "%08x", 64: "%016x"}[params(fmt)["bits"]]
    lines.append("msf%s_augmented_%s - %s %s -> %s %s %02x %s" % (
        fmt[1:], op, hx % a, hx % b, hx % head, hx % tail, flags, prov))
    return info


def enc(fmt, sign, mag, exp):
    bits = encode_exact(fmt, sign, mag, exp)
    assert bits is not None, (fmt, sign, mag, exp)
    return bits


def pow2(fmt, e, sign=0):
    return enc(fmt, sign, 1, e)


def with_signs(vals):
    out = []
    for v in vals:
        out.append(v)
    return sorted(set(out))


def neg(fmt, x):
    return x ^ params(fmt)["sign"]


def boundary_pool(fmt):
    q = params(fmt)
    p, t, emin, emax = q["p"], q["t"], q["emin"], q["emax"]
    sigs = [1 << (p - 1), (1 << (p - 1)) + 1, (1 << p) - 1,
            (1 << p) - 2, (1 << (p - 1)) + (1 << (p - 2))]
    vals = [0, q["sign"]]
    for m in (1, 2, 3, (1 << (p - 1)) - 1, 1 << (p - 1)):
        vals.append(enc(fmt, 0, m, q["u0e"]))
    for e in (emin, emin + 1, emin + 2, -2, -1, 0, 1, 2,
              emax - 1, emax):
        for s in sigs:
            vals.append(enc(fmt, 0, s, e - p + 1))
    vals += [q["inf"], q["qnan"], q["qnan"] | 1,
             q["inf"] | 1, q["inf"] | (q["qbit"] - 1)]
    out = sorted(set(vals))
    return sorted(set(out + [neg(fmt, v) for v in out]))


def factor_pair(fmt, nbits_value):
    """Factor 2^(p+1)-1 as A*B with both factors fitting p
    bits, by the algebraic divisor of p+1 (12/25/54 are all
    composite). Used for exact mul overflow-threshold ties."""
    q = params(fmt)
    n = nbits_value
    assert n == (1 << (q["p"] + 1)) - 1
    d = next(d for d in range(2, q["p"] + 1) if (q["p"] + 1) % d == 0)
    a = (1 << d) - 1
    b = n // a
    assert a * b == n and a.bit_length() <= q["p"]
    assert b.bit_length() <= q["p"], (fmt, a, b)
    return a, b


def collect(lines, seen, fmt, candidates, op, pred, quota, label):
    """Emit first `quota` candidates satisfying pred(info,
    head, tail); generation refuses if the quota is short."""
    n = 0
    for a, b in candidates:
        if n >= quota:
            break
        head, tail, flags, info = ref_augmented(fmt, a, b, op)
        if not pred(fmt, a, b, head, tail, flags, info):
            continue
        before = len(lines)
        emit(lines, seen, fmt, a, b, op, PROV_D)
        n += len(lines) - before
    assert n >= quota, (fmt, label, n, quota)
    return n


def generate_fmt(fmt):
    q = params(fmt)
    p, emin, emax = q["p"], q["emin"], q["emax"]
    lines, seen, fam = [], set(), {}

    def section(label):
        fam[label] = fam.get(label, 0)
        return len(lines)

    def close(label, start):
        fam[label] += len(lines) - start

    pool = boundary_pool(fmt)
    # Directed families emit first so their per-family
    # counts are not dedup-starved by the pool cross
    # product, which runs after them (below).

    # Specials matrix in both orders.
    specials = [0, q["sign"], q["inf"], neg(fmt, q["inf"]),
                q["qnan"], neg(fmt, q["qnan"] | 5), q["qnan"] | 1,
                q["inf"] | 1, neg(fmt, q["inf"] | 3),
                q["inf"] | (q["qbit"] - 1),
                pow2(fmt, 0), pow2(fmt, 0, 1),
                enc(fmt, 0, 1, q["u0e"]), enc(fmt, 1, 1, q["u0e"])]
    st = section("specials-twice")
    for a in specials:
        for b in specials:
            for op in OPS:
                emit(lines, seen, fmt, a, b, op, PROV_D)
                emit(lines, seen, fmt, b, a, op, PROV_D)
    close("specials-twice", st)

    # RTTZ tie discriminators, add/sub constructed at
    # several binades including both binade boundaries.
    st = section("rttz-ties")
    tie_exps = sorted({emin + 1, emin + 2, -1, 0, 1, 7,
                       emax - 2, emax - 1})
    for e in tie_exps:
        for s in (1 << (p - 1), (1 << (p - 1)) + 1, (1 << p) - 2):
            x = enc(fmt, 0, s, e - p + 1)
            half = encode_exact(fmt, 0, 1, e - p)  # ulp(x)/2
            if half is None:
                continue
            for a, b, op in ((x, half, "add"), (neg(fmt, x), half, "add"),
                             (x, half, "sub"), (x, neg(fmt, half), "sub")):
                # at a binade start, x - ulp/2 is the exact
                # predecessor (finer grid below), not a tie;
                # the checker decides each line either way
                emit(lines, seen, fmt, a, b, op, PROV_D)
        # binade crossing: x a power of two, step below is
        # half the step above; half that step is a tie.
        x = pow2(fmt, e)
        y = encode_exact(fmt, 0, 1, e - p - 1)
        if y is not None:
            emit(lines, seen, fmt, x, y, "sub", PROV_D)
            emit(lines, seen, fmt, x, neg(fmt, y), "add", PROV_D)
    # mul ties: algebraic family (2^(p-1)+2^s)(2^(p-1)+
    # 2^t) with s+t = p-2 leaves exactly the half bit set
    # in the dropped low half of the product; the exact
    # midpoint predicate in collect verifies each one.
    candidates = []
    base = 1 << (p - 1)
    for s in range(1, p - 2):
        a = enc(fmt, 0, base + (1 << s), -p + 1)
        b = enc(fmt, 0, base + (1 << (p - 2 - s)), -p + 1)
        candidates += [(a, b), (neg(fmt, a), b), (a, neg(fmt, b))]
    for da in range(0, 130, 7):
        for db in range(0, 130, 11):
            a = enc(fmt, 0, base + da, -p + 1)
            b = enc(fmt, 0, base + db, -p + 1)
            candidates += [(a, b), (neg(fmt, a), b)]
    st2 = len(lines)
    collect(lines, seen, fmt, candidates, "mul",
            lambda f, a, b, h, t, fl, i: i["exact"] is not None
            and i["kind"] in ("pair-exact", "tiny-exact")
            and is_tie(f, i["exact"], h), 8, "mul-ties")
    close("rttz-ties", st)
    fam["mul-ties(search)"] = len(lines) - st2

    # Overflow threshold: tie (delivers max-finite with a
    # half-ulp tail, no flags), one step above (inf pair,
    # overflow+inexact), one step below.
    st = section("overflow-threshold")
    maxfin = enc(fmt, 0, (1 << p) - 1, emax - p + 1)
    half_ulp_max = pow2(fmt, emax - p)
    hv_sig = 1 << (p - 1)
    above = enc(fmt, 0, hv_sig + 1, emax - p - (p - 1))
    below = enc(fmt, 0, hv_sig - 1, emax - p - (p - 1)) if p > 2 else None
    for y in (half_ulp_max, above, below):
        if y is None:
            continue
        for a, b, op in ((maxfin, y, "add"), (neg(fmt, maxfin), neg(fmt, y), "add"),
                         (maxfin, neg(fmt, y), "sub"), (neg(fmt, maxfin), y, "sub")):
            emit(lines, seen, fmt, a, b, op, PROV_D)
    fa, fb = factor_pair(fmt, (1 << (p + 1)) - 1)
    ta = enc(fmt, 0, fa, emax - p)
    tb = enc(fmt, 0, fb, 0)
    info = emit(lines, seen, fmt, ta, tb, "mul", PROV_D)
    assert info is not None and info["kind"] == "pair-exact", (fmt, info)
    emit(lines, seen, fmt, neg(fmt, ta), tb, "mul", PROV_D)
    tb_up = enc(fmt, 0, fb + (1 << max(0, fb.bit_length() - (p - 1))), 0)
    emit(lines, seen, fmt, ta, tb_up, "mul", PROV_D)
    close("overflow-threshold", st)

    # Huge-gap verbatim pairs and span-boundary ladders.
    st = section("verbatim")
    minsub = enc(fmt, 0, 1, q["u0e"])
    maxsub = enc(fmt, 0, (1 << (p - 1)) - 1, q["u0e"])
    for e in sorted({emin, emin + 3, -1, 0, 40, emax - 1, emax}):
        if not (emin <= e <= emax):
            continue
        x = enc(fmt, 0, (1 << p) - 1, e - p + 1)
        for y in (minsub, maxsub, neg(fmt, minsub)):
            for op in ("add", "sub"):
                emit(lines, seen, fmt, x, y, op, PROV_D)
                emit(lines, seen, fmt, y, x, op, PROV_D)
    for gap in (120, 126, 127, 128, 129, 140, 200):
        e_hi, e_lo = gap // 2, gap // 2 - gap
        if not (emin <= e_lo and e_hi <= emax):
            continue
        x, y = pow2(fmt, e_hi), enc(fmt, 0, (1 << p) - 1, e_lo - p + 1)
        for op in ("add", "sub"):
            emit(lines, seen, fmt, x, y, op, PROV_D)
            emit(lines, seen, fmt, x, neg(fmt, y), op, PROV_D)
    close("verbatim", st)

    # Zero signs: every signed-zero combination, exact
    # cancellation, product signs, products rounding to 0.
    st = section("zero-signs")
    one = pow2(fmt, 0)
    three = enc(fmt, 0, 3 << (p - 2), -p + 1)
    for a in (0, q["sign"]):
        for b in (0, q["sign"], one, neg(fmt, one), minsub,
                  neg(fmt, minsub)):
            for op in OPS:
                emit(lines, seen, fmt, a, b, op, PROV_D)
                emit(lines, seen, fmt, b, a, op, PROV_D)
    for x in (one, three, maxfin, enc(fmt, 0, 2, q["u0e"])):
        for a, b, op in ((x, x, "sub"), (x, neg(fmt, x), "add"),
                         (neg(fmt, x), neg(fmt, x), "sub"),
                         (neg(fmt, x), x, "add")):
            emit(lines, seen, fmt, a, b, op, PROV_D)
    close("zero-signs", st)

    # Tiny exact residuals (the P1 cells): directed add
    # construction plus exact search quotas per operation.
    st = section("p1-tiny-exact")
    if emin + p <= emax:
        x = pow2(fmt, emin + p)
        for y in (maxsub, minsub, enc(fmt, 0, 3, q["u0e"])):
            for a, b, op in ((x, y, "add"), (x, y, "sub"),
                             (neg(fmt, x), y, "add")):
                emit(lines, seen, fmt, a, b, op, PROV_D)
    tiny_cands = []
    small = [enc(fmt, 0, m, q["u0e"])
             for m in (1, 2, 3, 5, 17, (1 << (p - 1)) - 1)]
    lifts = []
    for e in (emin, emin + p - 1, emin + p, emin + p + 2, -3):
        if emin <= e <= emax:
            lifts += [pow2(fmt, e),
                      enc(fmt, 0, (1 << (p - 1)) + 1, e - p + 1),
                      enc(fmt, 0, (1 << p) - 1, e - p + 1)]
    for a in small + lifts:
        for b in small + lifts + [one, three]:
            tiny_cands += [(a, b), (neg(fmt, a), b)]
    for op in OPS:
        collect(lines, seen, fmt, tiny_cands, op,
                lambda f, a, b, h, t, fl, i: i["kind"] == "tiny-exact"
                and fl == 0, 6, "p1-%s" % op)
    close("p1-tiny-exact", st)

    # Mul below-step cells: unrepresentable residuals,
    # including tails rounding to zero and to min normal.
    st = section("mul-below-step")
    below_cands = []
    near = [one, enc(fmt, 0, 3 << (p - 2), -p),  # 0.75
            pow2(fmt, -1), enc(fmt, 0, (1 << p) - 1, -p),
            pow2(fmt, emin), enc(fmt, 0, (1 << (p - 1)) + 1, -p + 1)]
    for a in small + [pow2(fmt, emin)]:
        for b in near + small:
            below_cands += [(a, b), (neg(fmt, a), b), (a, neg(fmt, b))]
    collect(lines, seen, fmt, below_cands, "mul",
            lambda f, a, b, h, t, fl, i: i["kind"] == "mul-inexact-tail",
            24, "below-step")
    sub = {}
    for label, pred in (
            ("tail-zero", lambda f, a, b, h, t, fl, i:
             i["kind"] == "mul-inexact-tail" and value_of(f, t) == 0),
            ("tail-zero-opp-head", lambda f, a, b, h, t, fl, i:
             i["kind"] == "mul-inexact-tail" and value_of(f, t) == 0
             and (t & params(f)["sign"]) != (h & params(f)["sign"])),
            ("tail-min-normal", lambda f, a, b, h, t, fl, i:
             i["kind"] == "mul-inexact-tail"
             and abs(value_of(f, t)) == Fraction(2) ** params(f)["emin"])):
        st2 = len(lines)
        try:
            collect(lines, seen, fmt, below_cands, "mul", pred,
                    1, "below-%s" % label)
            sub[label] = len(lines) - st2
        except AssertionError:
            sub[label] = 0
    fam["mul-below-step-sub"] = sub
    close("mul-below-step", st)

    st = section("pool-cross")
    for a in pool:
        for b in pool:
            for op in OPS:
                emit(lines, seen, fmt, a, b, op, PROV_D)
    close("pool-cross", st)

    # Seeded sweeps: raw encodings, finite-biased, close
    # exponents, tiny-biased. One seed per format.
    st = section("seeded")
    rng = random.Random({"f16": 2026102901, "f32": 2026102902,
                         "f64": 2026102903}[fmt])
    bits = q["bits"]
    exp_mask = q["emaxf"] << q["t"]
    for i in range(2600):
        kind = i % 4
        a = rng.getrandbits(bits)
        b = rng.getrandbits(bits)
        if kind == 1:
            a = (a & ~exp_mask) | (rng.randrange(q["emaxf"]) << q["t"])
            b = (b & ~exp_mask) | (rng.randrange(q["emaxf"]) << q["t"])
        elif kind == 2:
            ea = (a >> q["t"]) & q["emaxf"]
            eb = min(max(ea + rng.randint(-3, 3), 0), q["emaxf"] - 1)
            b = (b & ~exp_mask) | (eb << q["t"])
            a = (a & ~exp_mask) | (min(ea, q["emaxf"] - 1) << q["t"])
        elif kind == 3:
            a = (a & ~exp_mask) | (rng.randrange(3) << q["t"])
            b = (b & ~exp_mask) | (rng.randrange(4) << q["t"])
        emit(lines, seen, fmt, a, b, OPS[i % 3], PROV_S)
    close("seeded", st)
    return lines, fam


def main(argv):
    if len(argv) != 2:
        print("usage: gen_vectors_aug.py OUTDIR")
        return 2
    outdir = Path(argv[1])
    outdir.mkdir(parents=True, exist_ok=True)
    for fmt in ("f16", "f32", "f64"):
        lines, fam = generate_fmt(fmt)
        header = [
            "# generated by tests/gen_vectors_aug.py - do not edit (regenerate)",
            "# expectations: project-exact Fraction reference in that file,",
            "# every line re-decided by its independent neighbour checker;",
            "# P1=R2 (exact tiny residual raises no flag, 7.5); Clause 9.5",
        ]
        text = "\n".join(header + lines) + "\n"
        path = outdir / ("aug-%s.vec" % fmt)
        path.write_bytes(text.encode("utf-8"))
        print("wrote %s (%d vectors)" % (path, len(lines)))
        for k in sorted(fam):
            print("  family %-24s %s" % (k, fam[k]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
