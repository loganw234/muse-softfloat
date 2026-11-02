#!/usr/bin/env python3
# 03_indref.py part 1: independent exact reference (fresh code).
# No imports from tests/gen_vectors*.py. Decodes f16/f32/f64 exactly,
# computes exactly over Fraction, packs once per dest with one
# rounding (te/tz/tp/tn). NaN matrix per SF-0 2.5 as restated in the
# parcel design entry (operand order, first-sNaN-wins, payload shift
# with truncate-to-default, sign of source).
import sys


def P2(k):
    return Fraction(2) ** k
from fractions import Fraction

P = {"f16": 11, "f32": 24, "f64": 53}
EMAX = {"f16": 15, "f32": 127, "f64": 1023}
EMIN = {"f16": -14, "f32": -126, "f64": -1022}
T = {"f16": 10, "f32": 23, "f64": 52}
EB = {"f16": 5, "f32": 8, "f64": 11}
FMT = {"f16": 0, "f32": 1, "f64": 2}

INV, DZ, OVF, UNF, INX = 0x01, 0x02, 0x04, 0x08, 0x10


class D:
    def __init__(self, fmt, bits):
        t = T[fmt]
        self.fmt, self.bits = fmt, bits
        self.sign = (bits >> (t + EB[fmt])) & 1
        expf = (bits >> t) & ((1 << EB[fmt]) - 1)
        frac = bits & ((1 << t) - 1)
        if expf == (1 << EB[fmt]) - 1:
            if frac == 0:
                self.cls = "inf"
            else:
                self.cls = "snan" if ((frac >> (t - 1)) & 1) == 0 else "qnan"
                self.payload = frac
        elif expf == 0:
            if frac == 0:
                self.cls = "zero"
            else:
                self.cls = "finite"
                self.val = Fraction(frac) * Fraction(2) ** (EMIN[fmt] - P[fmt] + 1)
        else:
            self.cls = "finite"
            self.val = Fraction((1 << t) + frac) * Fraction(2) ** (expf - bias(fmt) - t)
        if self.cls == "finite" and self.sign == 1:
            self.val = -self.val


def bias(fmt):
    return 2 ** (EB[fmt] - 1) - 1


def round_int(q, rm, sign):
    # round nonzero Fraction q>0 to int under rm (sign: 0 pos, 1 neg)
    fl = q.numerator // q.denominator
    rem = q - fl
    if rem == 0:
        return fl, False
    if rm == "te":
        c = fl + 1
        d = c - q
        if rem < d:
            return fl, True
        if d < rem:
            return c, True
        return (c if (fl & 1) else fl), True
    if rm == "tz":
        return fl, True
    if rm == "tp":
        return (fl + 1 if sign == 0 else fl), True
    if rm == "tn":
        return (fl if sign == 0 else fl + 1), True
    raise ValueError(rm)


def pack(dest, v, rm, zsign=0):
    """Round exact Fraction v once to dest. Returns (bits, flags)."""
    p, emax, emin = P[dest], EMAX[dest], EMIN[dest]
    t = T[dest]
    if v == 0:
        return (zsign << (t + EB[dest])), 0
    s = 0 if v > 0 else 1
    m = abs(v)
    # unbounded exponent: m = f * 2^e, 1 <= f < 2
    e = m.numerator.bit_length() - m.denominator.bit_length()
    while m >= P2(e + 1):
        e += 1
    while m < P2(e):
        e -= 1
    if e >= emin:
        # normal path: round mantissa to p bits
        q = m / P2(e - p + 1)
        sig, inx = round_int(q, rm, s)
        if sig >= (1 << p):
            sig >>= 1
            e += 1
        if e > emax:  # overflow
            if (rm == "tz") or (rm == "tp" and s == 1) or (rm == "tn" and s == 0):
                # maxfinite: expfield max-1, all frac bits
                bits = (s << (t + EB[dest])) | ((((1 << EB[dest]) - 2) << t) | ((1 << t) - 1))
                return bits, OVF | INX
            bits = (s << (t + EB[dest])) | (((1 << EB[dest]) - 1) << t)
            return bits, OVF | INX
        frac = sig - (1 << (p - 1))
        bits = (s << (t + EB[dest])) | ((e + bias(dest)) << t) | frac
        if inx:
            # tininess after rounding: rounded result subnormal?
            if e < emin:
                return bits, UNF | INX
            return bits, INX
        return bits, 0
    else:
        # subnormal path: quantum is 2^(emin-p+1)
        q = m / P2(emin - p + 1)
        sig, inx = round_int(q, rm, s)
        if sig >= (1 << (p - 1)):
            # carries into normal range
            e2 = emin
            frac = sig - (1 << (p - 1))
            bits = (s << (t + EB[dest])) | ((e2 + bias(dest)) << t) | frac
            return (bits, INX) if inx else (bits, 0)
        if sig == 0:
            return (s << (t + EB[dest])), (INX | UNF) if inx else 0
        bits = (s << (t + EB[dest])) | sig
        return bits, (UNF | INX) if inx else 0


def default_nan(dest):
    return (((1 << EB[dest]) - 1) << T[dest]) | (1 << (T[dest] - 1))


def deliver(dest, d, snan):
    """Map operand NaN d into dest. sNaN (quieted): the quiet bit is
    stripped before the field shift; a zero mapped payload delivers
    the positive default quiet NaN, else sign|inf|mapped|quiet.
    qNaN: quiet bit included in the shift (narrowing never clears the
    dest quiet bit), sign always preserved. Calibrated: sNaN
    0xFFF0000000000001 -> 0x7fc00000; qNaN 0xFFF8000010000000 ->
    0xffc00000."""
    t, ts = T[dest], T[d.fmt]
    sh = t - ts
    if snan:
        q = d.payload & ~(1 << (ts - 1))
        q = (q << sh) if sh >= 0 else (q >> (-sh))
        q &= (1 << t) - 1
        if q == 0:
            return default_nan(dest)
        return ((d.sign << (t + EB[dest])) | (((1 << EB[dest]) - 1) << t)
                | q | (1 << (t - 1)))
    q = (d.payload | (1 << (ts - 1))) & ((1 << ts) - 1)
    q = (q << sh) if sh >= 0 else (q >> (-sh))
    q &= (1 << t) - 1
    return ((d.sign << (t + EB[dest])) | (((1 << EB[dest]) - 1) << t) | q)


def nan_pick(dest, ops):
    """ops: list of D in operand order. Returns (bits, invalid?) or None."""
    for d in ops:
        if d.cls == "snan":
            return deliver(dest, d, True), True
    for d in ops:
        if d.cls == "qnan":
            return deliver(dest, d, False), False
    return None


def ref_addsub(dest, afmt, a, bfmt, b, sub, rm):
    A, B = D(afmt, a), D(bfmt, b)
    pk = nan_pick(dest, [A, B])
    if pk:
        return pk[0], (INV if pk[1] else 0)
    bsign = B.sign ^ (1 if sub else 0)
    if A.cls == "inf" or B.cls == "inf":
        if A.cls == "inf" and B.cls == "inf" and A.sign != bsign:
            return default_nan(dest), INV
        s = A.sign if A.cls == "inf" else bsign
        return (s << (T[dest] + EB[dest])) | (((1 << EB[dest]) - 1) << T[dest]), 0
    aval = Fraction(0) if A.cls == "zero" else A.val
    bval = Fraction(0) if B.cls == "zero" else B.val
    v = aval + (-bval if sub else bval)
    if v == 0:
        if A.sign == bsign:
            zs = A.sign
        else:
            zs = 1 if rm == "tn" else 0
        return (zs << (T[dest] + EB[dest])), 0
    return pack(dest, v, rm)


def ref_mul(dest, afmt, a, bfmt, b, rm):
    A, B = D(afmt, a), D(bfmt, b)
    pk = nan_pick(dest, [A, B])
    if pk:
        return pk[0], (INV if pk[1] else 0)
    az = A.cls == "zero"
    bz = B.cls == "zero"
    ai = A.cls == "inf"
    bi = B.cls == "inf"
    if (az and bi) or (ai and bz):
        return default_nan(dest), INV
    s = A.sign ^ B.sign
    if ai or bi:
        return (s << (T[dest] + EB[dest])) | (((1 << EB[dest]) - 1) << T[dest]), 0
    if az or bz:
        return (s << (T[dest] + EB[dest])), 0
    return pack(dest, A.val * B.val, rm)


def ref_div(dest, afmt, a, bfmt, b, rm):
    A, B = D(afmt, a), D(bfmt, b)
    pk = nan_pick(dest, [A, B])
    if pk:
        return pk[0], (INV if pk[1] else 0)
    az = A.cls == "zero"
    bz = B.cls == "zero"
    ai = A.cls == "inf"
    bi = B.cls == "inf"
    s = A.sign ^ B.sign
    if (az and bz) or (ai and bi):
        return default_nan(dest), INV
    if ai or bz:
        if bz and not ai and not az:
            return (s << (T[dest] + EB[dest])) | (((1 << EB[dest]) - 1) << T[dest]), DZ
        return (s << (T[dest] + EB[dest])) | (((1 << EB[dest]) - 1) << T[dest]), 0
    if bi or az:
        return (s << (T[dest] + EB[dest])), 0
    return pack(dest, A.val / B.val, rm)


def ref_sqrt(dest, afmt, a, rm):
    A = D(afmt, a)
    if A.cls == "snan":
        return deliver(dest, A, True), INV
    if A.cls == "qnan":
        return deliver(dest, A, False), 0
    if A.cls == "zero":
        return (A.sign << (T[dest] + EB[dest])), 0
    if A.sign == 1 and (A.cls == "inf" or A.val != 0):
        return default_nan(dest), INV
    if A.cls == "inf":
        return ((((1 << EB[dest]) - 1) << T[dest])), 0
    import math
    p = P[dest]
    # scale v into [1,4): v = vv * 4^(-e); sqrt(v) = sqrt(vv) * 2^e
    e, vv = 0, A.val
    while vv >= 2:
        vv /= 4
        e += 1
    while vv < 1:
        vv *= 4
        e -= 1
    approx = math.sqrt(float(vv)) * (1 << (p - 1))
    best = int(approx) - 3
    while Fraction(best + 1, 1 << (p - 1)) ** 2 <= vv:
        best += 1
    while Fraction(best, 1 << (p - 1)) ** 2 > vv:
        best -= 1
    unit = Fraction(1, 1 << (p - 1))
    blo = Fraction(best, 1 << (p - 1))
    if blo * blo == vv:
        probe = blo  # exact
    elif (blo + unit / 2) ** 2 == vv:
        probe = blo + unit / 2  # exact tie
    elif (blo + unit / 2) ** 2 > vv:
        probe = blo + unit / 4  # below the tie: rounds like best+epsilon
    else:
        probe = blo + unit * 3 / 4  # above the tie
    return pack(dest, probe * P2(e), rm)


def ref_fma(dest, afmt, a, bfmt, b, cfmt, c, rm):
    A, B, C = D(afmt, a), D(bfmt, b), D(cfmt, c)
    for d in (A, B, C):
        if d.cls == "snan":
            return deliver(dest, d, True), INV
    az = A.cls == "zero"
    bz = B.cls == "zero"
    ai = A.cls == "inf"
    bi = B.cls == "inf"
    if (az and bi) or (ai and bz):
        if C.cls == "qnan":
            return deliver(dest, C, True), INV
        return default_nan(dest), INV
    for d in (A, B, C):
        if d.cls == "qnan":
            return deliver(dest, d, False), 0
    if ai or bi:
        ps = A.sign ^ B.sign
        if C.cls == "inf" and C.sign != ps:
            return default_nan(dest), INV
        if C.cls == "inf":
            return ((C.sign << (T[dest] + EB[dest]))
                    | (((1 << EB[dest]) - 1) << T[dest])), 0
        return ((ps << (T[dest] + EB[dest]))
                | (((1 << EB[dest]) - 1) << T[dest])), 0
    if C.cls == "inf":
        return ((C.sign << (T[dest] + EB[dest])) | (((1 << EB[dest]) - 1) << T[dest])), 0
    # all finite (zeros included): exact product + addend, one pack
    av = Fraction(0) if A.cls == "zero" else A.val
    bv = Fraction(0) if B.cls == "zero" else B.val
    cv = Fraction(0) if C.cls == "zero" else C.val
    v = av * bv + cv
    if v == 0:
        # sign of exact zero fma: product-zero + addend-zero rules
        if C.cls == "zero" and (az or bz):
            ps = (A.sign ^ B.sign) if (az or bz) else 0
            if C.sign == ps:
                zs = C.sign
            else:
                zs = 1 if rm == "tn" else 0
            return (zs << (T[dest] + EB[dest])), 0
        if C.cls == "zero":
            return ((A.sign ^ B.sign) << (T[dest] + EB[dest])), 0
        if az or bz:
            return (C.sign << (T[dest] + EB[dest])), 0
        zs = 1 if rm == "tn" else 0
        return (zs << (T[dest] + EB[dest])), 0
    return pack(dest, v, rm)


def ref_conv(dest, afmt, a, rm):
    A = D(afmt, a)
    if A.cls == "snan":
        return deliver(dest, A, True), INV
    if A.cls == "qnan":
        return deliver(dest, A, False), 0
    if A.cls == "inf":
        return ((A.sign << (T[dest] + EB[dest])) | (((1 << EB[dest]) - 1) << T[dest])), 0
    if A.cls == "zero":
        return (A.sign << (T[dest] + EB[dest])), 0
    return pack(dest, A.val, rm)


REL_LT, REL_EQ, REL_GT, REL_UN = 1, 2, 4, 8


def ref_compare(dest, a, bfmt, b, mask, signaling):
    A, B = D(dest, a), D(bfmt, b)
    nan = A.cls in ("snan", "qnan") or B.cls in ("snan", "qnan")
    if nan:
        inv = signaling or A.cls == "snan" or B.cls == "snan"
        return (1 if (mask & REL_UN) else 0), (INV if inv else 0)
    if A.cls == "inf" or B.cls == "inf":
        if A.cls == "inf" and B.cls == "inf":
            rel = REL_EQ if A.sign == B.sign else (REL_LT if A.sign else REL_GT)
        elif A.cls == "inf":
            rel = REL_LT if A.sign else REL_GT
        else:
            rel = REL_GT if B.sign else REL_LT
    elif A.cls == "zero" and B.cls == "zero":
        rel = REL_EQ
    elif A.cls == "zero":
        rel = REL_LT if B.val > 0 else REL_GT
    elif B.cls == "zero":
        rel = REL_GT if A.val > 0 else REL_LT
    else:
        rel = REL_LT if A.val < B.val else (REL_GT if A.val > B.val else REL_EQ)
    return (1 if (mask & rel) else 0), 0


CMP = {
    "quiet_equal": (REL_EQ, 0), "quiet_not_equal": (REL_LT | REL_GT | REL_UN, 0),
    "signaling_equal": (REL_EQ, 1), "signaling_not_equal": (REL_LT | REL_GT | REL_UN, 1),
    "quiet_greater": (REL_GT, 0), "quiet_greater_equal": (REL_GT | REL_EQ, 0),
    "quiet_less": (REL_LT, 0), "quiet_less_equal": (REL_LT | REL_EQ, 0),
    "quiet_not_greater": (REL_LT | REL_EQ | REL_UN, 0),
    "quiet_not_less": (REL_GT | REL_EQ | REL_UN, 0),
    "quiet_less_unordered": (REL_LT | REL_UN, 0),
    "quiet_greater_unordered": (REL_GT | REL_UN, 0),
    "quiet_unordered": (REL_UN, 0), "quiet_ordered": (REL_LT | REL_EQ | REL_GT, 0),
    "signaling_greater": (REL_GT, 1), "signaling_greater_equal": (REL_GT | REL_EQ, 1),
    "signaling_less": (REL_LT, 1), "signaling_less_equal": (REL_LT | REL_EQ, 1),
    "signaling_not_greater": (REL_LT | REL_EQ | REL_UN, 1),
    "signaling_not_less": (REL_GT | REL_EQ | REL_UN, 1),
    "signaling_less_unordered": (REL_LT | REL_UN, 1),
    "signaling_greater_unordered": (REL_GT | REL_UN, 1),
}


def dispatch(name, rm, args):
    d = "f32" if name[3:6] == "32_" else "f64"
    rest = name[6:]
    if rest.startswith("compare_"):
        pred = rest[len("compare_"):][:-4]
        mask, sig = CMP[pred]
        return ref_compare(d, args[0], "f16", args[1], mask, sig)
    fam2 = rest.split("_")
    if fam2[0] in ("add", "sub"):
        return ref_addsub(d, fam2[1], args[0], fam2[2], args[1], fam2[0] == "sub", rm)
    if fam2[0] == "mul":
        return ref_mul(d, fam2[1], args[0], fam2[2], args[1], rm)
    if fam2[0] == "div":
        return ref_div(d, fam2[1], args[0], fam2[2], args[1], rm)
    if fam2[0] == "sqrt":
        return ref_sqrt(d, fam2[1], args[0], rm)
    if fam2[0] == "from":
        return ref_conv(d, fam2[1], args[0], rm)
    if fam2[0] == "fma":
        return ref_fma(d, fam2[1], args[0], fam2[2], args[1], fam2[3], args[2], rm)
    raise ValueError(name)


def parse_vec(path):
    out = []
    for i, ln in enumerate(open(path, encoding="utf-8")):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        t = ln.split()
        op, rm = t[0], t[1]
        ai = t.index("->")
        args = [int(x, 16) for x in t[2:ai]]
        bits, flags = int(t[ai + 1], 16), int(t[ai + 2], 16)
        out.append((i + 1, op, rm, args, bits, flags, ln))
    return out


def calib(root):
    import collections
    files = ["arith-xf.vec", "fma-sqrt-xf.vec", "conv-xf.vec", "compare-xf.vec", "traps-xf.vec"]
    tot = bad = 0
    byop = collections.Counter()
    for f in files:
        for (ln, op, rm, args, bits, flags, raw) in parse_vec(root + "/tests/vectors/" + f):
            tot += 1
            eb, ef = dispatch(op, rm, args)
            if eb != bits or ef != flags:
                bad += 1
                byop[op] += 1
                if bad <= 8:
                    print("MISMATCH %s:%d got %x/%02x want %x/%02x | %s" % (
                        f, ln, eb, ef, bits, flags, raw[:150]))
    print("calib: %d checked, %d mismatches vs committed" % (tot, bad))
    for op, n in sorted(byop.items()):
        print("  %d %s" % (n, op))


def edge_pool(fmt, rng):
    # deterministic edge-heavy pool, independent of the parcel generator
    t = T[fmt]
    inf = ((1 << EB[fmt]) - 1) << t
    out = [0, 1 << (t + EB[fmt]), 1, (1 << (t + EB[fmt])) | 1, (1 << t) - 1,
           inf - (1 << t), inf, inf | (1 << (t + EB[fmt])),
           inf | (1 << (t - 1)), inf | 1, inf | (1 << (t - 1)) - 1,
           inf | (1 << (t + EB[fmt])) | 1]
    # 1.0, 2^p, 2^p-1, ties, f32-boundary values where encodable
    one = None
    for v in [Fraction(1), Fraction(2), Fraction(1, 2), Fraction(3, 2),
              Fraction(1) + Fraction(1, 2 ** (P[fmt] - 1)),
              Fraction(1) + Fraction(1, 2 ** P[fmt]),
              Fraction(65504), Fraction(1, 3), Fraction(1, 10)]:
        try:
            b, fl = pack(fmt, v, "te")
            if fl == 0:
                out.append(b)
                if v == 1:
                    one = b
            b, fl = pack(fmt, -v, "te")
            if fl == 0:
                out.append(b)
        except Exception:
            pass
    # danger values: nonzero low bits for f64, odd bits for f32
    for b in [0x3FF0000000000001, 0x3FF0000010000000, 0xBFEFFFFFFFFFFFFF,
              0x3690000000000000, 0x0000000000000001, 0x000FFFFFFFFFFFFF,
              0x3F800001, 0x3DCCCCCD, 0x7F7FFFFF, 0x00800000, 0x3C00, 0x8400]:
        out.append(b & ((1 << (2 * T[fmt] + EB[fmt])) - 1))
    # dedupe, keep order
    seen, pool = set(), []
    for b in out:
        if b not in seen:
            seen.add(b)
            pool.append(b)
    return pool


def wrong_convert_first(dest, fam, fmts, args, rm):
    # convert each source to f32 first (line rm), then operate in f32
    c2 = []
    for fmt, a in zip(fmts, args):
        b2, _ = ref_conv("f32", fmt, a, rm)
        c2.append(b2)
    return dispatch("msf32_%s_%s" % (fam, "_".join(["f32"] * len(fmts))), rm, c2)


def wrong_unfused(dest, fmts, args, rm):
    p, _ = ref_mul(dest, fmts[0], args[0], fmts[1], args[1], rm)
    return ref_addsub(dest, dest, p, fmts[2], args[2], False, rm)


def wrong_via_f32(dest, fam, fmts, args, rm):
    r, _ = dispatch("msf32_%s_%s" % (fam, "_".join(fmts)), rm, args)
    return ref_conv(dest, "f32", r, rm)


def sweep(root, outdir, seed, dest):
    import random
    rng = random.Random(seed)
    pools = {f: edge_pool(f, rng) for f in ("f16", "f32", "f64")}
    rows = [l.rstrip().split("\t") for l in
            open(root + "/docs/COVERAGE.tsv", encoding="utf-8")
            if l.strip() and not l.startswith("#")]
    hdr = rows[0]
    idx = {h: i for i, h in enumerate(hdr)}
    names = [r[idx["name"]] for r in rows[1:]
              if r[idx["wave"]] == "2" and r[idx["name"]].startswith("msf%s_" % dest[1:])]
    assert len(names) == 63, len(names)
    lines, exposing, counts = [], {}, {}
    for n in names:
        rest = n[6:]
        if rest.startswith("compare_"):
            pred = rest[len("compare_"):][:-4]
            op = ("compare",)
            fmts = (dest, "f16")
        else:
            p = rest.split("_")
            op, fmts = tuple([p[0]] + p[1:]), tuple(p[1:])
        made = exp = 0
        tries = 0
        while made < 40 and tries < 4000:
            tries += 1
            rm = "-" if op == ("compare",) else ["te", "tz", "tp", "tn"][rng.randrange(4)]
            args = [rng.choice(pools[f]) for f in fmts]
            eb, ef = dispatch(n, rm, args)
            # exposing: some operand decodes differently under another format
            xp = False
            for fmt, a in zip(fmts, args):
                v0 = canon(fmt, a)
                for of in ("f16", "f32", "f64"):
                    if of == fmt:
                        continue
                    if canon(of, a & ((1 << width(of)) - 1)) != v0:
                        xp = True
            if xp:
                exp += 1
            lines.append("%s %s %s -> %x %02x exact-py-vx:sweep-%s-%d" % (
                n, rm, " ".join("%x" % a for a in args), eb, ef, dest, seed))
            made += 1
        counts[n] = made
        exposing[n] = exp
    import os
    os.makedirs(outdir, exist_ok=True)
    with open("%s/sweep-%s-%d.vec" % (outdir, dest, seed), "w", encoding="utf-8") as f:
        f.write("# generated by verifier-w2xf 03_indref.py - independent reference\n")
        f.write("\n".join(lines) + "\n")
    print("sweep %s seed %d: %d lines, %d names" % (dest, seed, len(lines), len(names)))
    lo = sorted(exposing.items(), key=lambda kv: kv[1])[:6]
    print("lowest exposing counts:", lo)
    print("total exposing: %d/%d" % (sum(exposing.values()), len(lines)))


def canon(fmt, bits):
    d = D(fmt, bits)
    if d.cls == "finite":
        return (d.cls, d.sign, d.val)
    if d.cls == "zero":
        return (d.cls, d.sign)
    if d.cls in ("snan", "qnan"):
        return (d.cls, d.sign, d.payload)
    return (d.cls, d.sign)


def width(fmt):
    return {"f16": 16, "f32": 32, "f64": 64}[fmt]


def wrong_for_line(op, rm, args, prov):
    d = "f32" if op[3:6] == "32_" else "f64"
    rest = op[6:].split("_")
    if rest[0] in ("add", "sub", "mul", "div"):
        fam, fmts = rest[0], tuple(rest[1:])
        conv = [ref_conv("f32", f, a, rm)[0] for f, a in zip(fmts, args)]
        if prov == "trap-convert-first":
            return dispatch("msf32_%s_%s" % (fam, "_".join(["f32"] * 2)), rm, conv)
        if prov == "trap-via-f32":
            r, _ = dispatch("msf32_%s_%s" % (fam, "_".join(fmts)), rm, args)
            return ref_conv(d, "f32", r, rm)
    elif rest[0] == "fma":
        fmts = tuple(rest[1:])
        if prov == "trap-unfused":
            return wrong_unfused(d, fmts, args, rm)
        if prov == "trap-via-f32":
            return wrong_via_f32(d, "fma", fmts, args, rm)
        if prov == "trap-convert-first":
            conv = [ref_conv("f32", f, a, rm)[0] for f, a in zip(fmts, args)]
            return dispatch("msf32_fma_f32_f32_f32", rm, conv)
    elif rest[0] == "sqrt":
        if prov == "trap-via-f32":
            r, _ = dispatch("msf32_sqrt_%s" % rest[1], rm, args)
            return ref_conv(d, "f32", r, rm)
    raise ValueError((op, prov))


def traps(root, outdir):
    import os
    lines = parse_vec(root + "/tests/vectors/traps-xf.vec")
    disc = nondisc = 0
    famdisc = {}
    for (ln, op, rm, args, bits, flags, raw) in lines:
        prov = raw.split("exact-py-xf:")[1].strip()
        wb, wf = wrong_for_line(op, rm, args, prov)
        key = (prov, op.split("_")[1], op[3:6])
        if (wb, wf) != (bits, flags):
            disc += 1
            famdisc[key] = famdisc.get(key, 0) + 1
        else:
            nondisc += 1
            print("NON-DISCRIMINATING %d | %s" % (ln, raw[:160]))
    print("traps: %d lines, %d discriminate, %d do not" % (len(lines), disc, nondisc))
    for k in sorted(famdisc):
        print("  %d %s" % (famdisc[k], k))


BUGGY = {"msf32_add_f16_f64", "msf32_fma_f16_f32_f64",
         "msf64_compare_signaling_less_f16"}


def mutants(root, outpath):
    import io
    lines = parse_vec(root + "/tests/vectors/traps-xf.vec")
    seen, out = set(), []
    for (ln, op, rm, args, bits, flags, raw) in lines:
        prov = raw.split("exact-py-xf:")[1].strip()
        fam = op.split("_")[1]
        key = (prov, fam, op[3:6])
        if key in seen or op in BUGGY:
            continue
        wb, wf = wrong_for_line(op, rm, args, prov)
        if (wb, wf) == (bits, flags):
            continue
        seen.add(key)
        t = raw.split()
        ai = t.index("->")
        t[ai + 1] = "%x" % wb
        t[ai + 2] = "%02x" % wf
        t[-1] = "exact-py-vx:mutant-flipped"
        out.append(" ".join(t))
    io.open(outpath, "w", encoding="utf-8", newline="\n").write(
        "# verifier-w2xf trap mutants: expectation flipped to wrong-pipeline answer\n"
        + "\n".join(out) + "\n")
    print("mutants: %d lines (%d groups)" % (len(out), len(seen)))
    for k in sorted(seen):
        print("  %s" % (k,))


def f64conv():
    """Corroborate the lead ruling: convert-to-f64-first is exact, i.e.
    never differs from exact-then-round for dest-f64 rows."""
    import random
    rng = random.Random(777)
    pools = edge_pool("f64", rng)
    p16 = edge_pool("f16", rng)
    p32 = edge_pool("f32", rng)
    import collections
    kinds = collections.Counter()
    diff = tot = 0
    fam = {"add": lambda d, f, a, r: ref_addsub(d, f[0], a[0], f[1], a[1], False, r),
           "sub": lambda d, f, a, r: ref_addsub(d, f[0], a[0], f[1], a[1], True, r),
           "mul": lambda d, f, a, r: ref_mul(d, f[0], a[0], f[1], a[1], r),
           "div": lambda d, f, a, r: ref_div(d, f[0], a[0], f[1], a[1], r)}
    cases = [(("add", ("f16", "f64")), ("add", ("f64", "f16")),
              ("sub", ("f16", "f64")), ("sub", ("f64", "f16")),
              ("mul", ("f16", "f64")), ("mul", ("f64", "f16")),
              ("div", ("f16", "f64")), ("div", ("f64", "f16")))]
    poolmap = {"f16": p16, "f32": p32, "f64": pools}
    for (op, fmts) in cases[0]:
        for _ in range(500):
            rm = ["te", "tz", "tp", "tn"][rng.randrange(4)]
            args = [rng.choice(poolmap[f]) for f in fmts]
            e = fam[op]("f64", fmts, args, rm)
            cr = [ref_conv("f64", f, a, rm) for f, a in zip(fmts, args)]
            c = [b for (b, fl) in cr]
            wbits, wfl = fam[op]("f64", ("f64", "f64"), c, rm)
            for (b, fl) in cr:
                wfl |= fl
            w = (wbits, wfl)
            tot += 1
            if e != w:
                diff += 1
                enan = (e[0] & 0x7FF0000000000000) == 0x7FF0000000000000 and \
                    (e[0] & 0xFFFFFFFFFFFFF) != 0
                wnan = (w[0] & 0x7FF0000000000000) == 0x7FF0000000000000 and \
                    (w[0] & 0xFFFFFFFFFFFFF) != 0
                kind = "nan-nan" if (enan and wnan) else "other"
                kinds[kind] += 1
                if diff <= 5:
                    print("DIFF", op, fmts, [hex(a) for a in args], rm, e, w)
    # sqrt sampled too
    for _ in range(500):
        rm = ["te", "tz", "tp", "tn"][rng.randrange(4)]
        a = rng.choice(p16)
        e = ref_sqrt("f64", "f16", a, rm)
        cb, cf = ref_conv("f64", "f16", a, rm)
        wb, wf = ref_sqrt("f64", "f64", cb, rm)
        w = (wb, wf | cf)
        tot += 1
        if e != w:
            diff += 1
    print("f64conv: %d cases, %d differences %s" % (tot, diff, dict(kinds)))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "calib":
        calib(sys.argv[2])
    elif mode == "sweep":
        sweep(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])
    elif mode == "traps":
        traps(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif mode == "mutants":
        mutants(sys.argv[2], sys.argv[3])
    elif mode == "f64conv":
        f64conv()

