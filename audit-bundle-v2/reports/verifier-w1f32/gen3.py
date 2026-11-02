#!/usr/bin/env python3
"""Verifier-w1f32 probe 3 generator: directed exact-rational attacks on the
project-exact wave-1 binary32 families. Uses ref3.py only. Emits .vec files
with provenance verifier-w1f32:probe3-<family> for replay by the copy's runner.
"""
import os
import random
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref3 import (RMS, ref_addsub, ref_mul, ref_div, ref_sqrt, ref_fma,
                  ref_rint, ref_next, ref_remainder, ref_scaleb, ref_logb,
                  ref_from_int, ref_to_int, ref_cmp, ref_total_order, PREDS, D)

PROV = "verifier-w1f32:probe3"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "p3")
os.makedirs(OUT, exist_ok=True)

F32_HAND = [
    0x00000000, 0x80000000, 0x00000001, 0x80000001, 0x007FFFFF, 0x807FFFFF,
    0x00800000, 0x80800000, 0x3F800000, 0xBF800000, 0x40000000, 0xC0000000,
    0x3FC00000, 0xBFC00000, 0x3F000000, 0xBF000000, 0x7F7FFFFF, 0xFF7FFFFF,
    0x33800000, 0xB3800000, 0x34000001, 0x4B7FFFFF, 0xCB800000,
    0x3F800001, 0x3F7FFFFF, 0xBF800001, 0xBF7FFFFF, 0x4B800001,
    0x7F800000, 0xFF800000,
    0x7FC00000, 0xFFC00000, 0x7FC00001, 0xFFC00001, 0x7FE00000, 0x7FFFFFFF,
    0x7F800001, 0xFF800001, 0x7FA00000, 0xFFA00000, 0x7FBFFFFF, 0x7FFFFF00 - 0x7F000000,
    0x00800001, 0x80800001, 0x00400000, 0x3F000001, 0xBF000001,
    0x4F000000, 0xCF000000, 0x53000000, 0xD3000000, 0x7F000001, 0xFF000001,
]
F32_QNAN = [0x7FC00000, 0xFFC00000, 0x7FC00001, 0xFFC00001, 0x7FE00000, 0xFFE00000,
            0x7FFFFFFF, 0xFFFFFF7F & 0xFFFFFFFF]
F32_SNAN = [0x7F800001, 0xFF800001, 0x7FA00000, 0xFFA00000, 0x7FBFFFFF, 0xFFBFFFFF,
            0x7F800002, 0x7FA00001]
# finite near-max edge (looks NaN-ish, is not): exercises div/sub extremes
F32_FINEDGE = [0x7F000001, 0xFF000001]
F32_TRUNC_PAY = [0x7FC00000 | p for p in (0, 1, 2, 0x100, 0x3FFFFF)]

F64_HAND = [
    0x0000000000000000, 0x8000000000000000, 0x0000000000000001, 0x8000000000000001,
    0x000FFFFFFFFFFFFF, 0x0010000000000000, 0x8010000000000000,
    0x3FF0000000000000, 0xBFF0000000000000, 0x4000000000000000, 0x3FF8000000000000,
    0x3FE0000000000000, 0x7FEFFFFFFFFFFFFF, 0xFFEFFFFFFFFFFFFF,
    0x7FF0000000000000, 0xFFF0000000000000,
    0x7FF8000000000000, 0xFFF8000000000000, 0x7FF8000000000001, 0xFFF8000000000001,
    0x7FF0000000000001, 0xFFF0000000000001, 0x7FF4000000000000,
    0x3FF0000000000001, 0xBFF0000000000001, 0x4000000000000001,
    0x3380000000000000, 0x3C90000000000000,
]

rng = random.Random(1234567)
F32_RAND = [rng.getrandbits(32) for _ in range(120)]
F64_RAND = [rng.getrandbits(64) for _ in range(120)]

# f64 values at exact f32 midpoints (double-rounding traps), exponents sampled
TRAPS = []
for ee in list(range(-140, 140, 11)) + [-149, -150, -126, -127, -125, 127, 128, 129]:
    for m in (1, 3, 7, 0xFFFFFF):
        # midpoint between adjacent f32 values at binade ee: (2m+1)*2^(ee-24)
        sig = 2 * m + 1
        if sig >= (1 << 25):
            continue
        v = Fraction(sig, 1 << 24) * (Fraction(2) ** ee)
        # encode exactly in f64: v = sig2 * 2^exp2 with sig2 < 2^53
        n, d = v.numerator, v.denominator
        bl = max(n.bit_length() - d.bit_length(), 0)
        # normalize: shift to < 53 bits
        import math as _m
        e2 = n.bit_length() - d.bit_length()
        shift = 52 - (n.bit_length() - 1 - (d.bit_length() - 1) if d > 1 else n.bit_length() - 1)
        # simpler: build f64 bits via frexp-style loop
        f = float(v) if -1022 <= e2 <= 1023 else None
        import struct
        if f is not None and Fraction(f) == v:
            TRAPS.append(struct.unpack("<Q", struct.pack("<d", f))[0])
TRAPS = sorted(set(TRAPS))
print("traps:", len(TRAPS), file=sys.stderr)

F32_POOL = sorted(set(F32_HAND + F32_RAND + [0x3F800000 | i for i in range(0, 64, 7)]))
F64_POOL = sorted(set(F64_HAND + F64_RAND + TRAPS))

lines = {}


def emit(fam, line):
    lines.setdefault(fam, []).append(line)


def hx(v, width=None):
    s = "%x" % (v & ((1 << width) - 1) if width else v)
    return s


def w_addsub():
    n = 0
    # homogeneous f32 (corroboration slice only; authority is Berkeley)
    for a in F32_POOL[::4]:
        for b in F32_POOL[::9]:
            for rm in RMS:
                for issub, fam, nm in ((0, "xarith-hom", "add"), (1, "xarith-hom", "sub")):
                    r, f = ref_addsub("f32", a, "f32", b, issub, rm)
                    emit(fam, "msf32_%s %s %s %s -> %s %02x %s:%s" % (nm, rm, hx(a), hx(b), hx(r), f, PROV, fam))
                    n += 1
    # cross-format
    combos = [(a, "f32", b, "f64") for a in F32_POOL[::3] for b in F64_POOL[::7]]
    combos += [(a, "f64", b, "f32") for a in F64_POOL[::3] for b in F32_POOL[::7]]
    combos += [(a, "f64", b, "f64") for a in F64_POOL[::5] for b in F64_POOL[::11]]
    for (a, af, b, bf) in combos:
        for rm in RMS:
            for issub, nm in ((0, "add"), (1, "sub")):
                op = "msf32_%s" % nm if (af, bf) == ("f32", "f32") else "msf32_%s_%s_%s" % (nm, af, bf)
                r, f = ref_addsub(af, a, bf, b, issub, rm)
                emit("xarith", "%s %s %s %s -> %s %02x %s:xarith" % (op, rm, hx(a), hx(b), hx(r), f, PROV))
                n += 1
    return n


def w_muldiv():
    n = 0
    combos = [(a, "f32", b, "f32") for a in F32_POOL[::9] for b in F32_POOL[::13]]
    combos += [(a, "f32", b, "f64") for a in F32_POOL[::5] for b in F64_POOL[::9]]
    combos += [(a, "f64", b, "f32") for a in F64_POOL[::5] for b in F32_POOL[::9]]
    combos += [(a, "f64", b, "f64") for a in F64_POOL[::7] for b in F64_POOL[::13]]
    for (a, af, b, bf) in combos:
        for rm in RMS:
            for nm, fn in (("mul", ref_mul), ("div", ref_div)):
                op = "msf32_%s" % nm if (af, bf) == ("f32", "f32") else "msf32_%s_%s_%s" % (nm, af, bf)
                fam = "xarith-hom" if (af, bf) == ("f32", "f32") else "xarith"
                r, f = fn(af, a, bf, b, rm)
                emit(fam, "%s %s %s %s -> %s %02x %s:%s" % (op, rm, hx(a), hx(b), hx(r), f, PROV, fam))
                n += 1
    return n


def w_sqrtfma():
    n = 0
    for (a, af) in [(x, "f32") for x in F32_POOL[::3]] + [(x, "f64") for x in F64_POOL[::5]]:
        op = "msf32_sqrt" if af == "f32" else "msf32_sqrt_f64"
        for rm in RMS:
            r, f = ref_sqrt(af, a, rm)
            emit("xarith", "%s %s %s -> %s %02x %s:xarith" % (op, rm, hx(a), hx(r), f, PROV))
            n += 1
    trip = [(a, "f32", b, "f32", c, "f32") for a in F32_POOL[::7] for b in F32_POOL[::11] for c in F32_POOL[::13]]
    trip += [(a, "f64", b, "f32", c, "f64") for a in F64_POOL[::9] for b in F32_POOL[::13] for c in F64_POOL[::17]]
    trip += [(a, "f32", b, "f64", c, "f32") for a in F32_POOL[::11] for b in F64_POOL[::9] for c in F32_POOL[::17]]
    for (a, af, b, bf, c, cf) in trip[:700]:
        if (af, bf, cf) == ("f32", "f32", "f32"):
            op = "msf32_fma"
        else:
            op = "msf32_fma_%s_%s_%s" % (af, bf, cf)
        for rm in ("te", "tz"):
            r, f = ref_fma(af, a, bf, b, cf, c, rm)
            fam = "xarith-hom" if (af, bf, cf) == ("f32", "f32", "f32") else "xarith"
            emit(fam, "%s %s %s %s %s -> %s %02x %s:%s" % (op, rm, hx(a), hx(b), hx(c), hx(r), f, PROV, fam))
            n += 1
    # FMA zero-times-infinity with addends (SF-0 2.5 ruling incl quiet-NaN addend)
    zxi = [(0x00000000, 0x7F800000), (0x80000000, 0xFF800000), (0x7F800000, 0x00000000),
           (0xFF800000, 0x80000000)]
    adds = [0x00000000, 0x80000000, 0x3F800000, 0x7F800000, 0x7FC00000, 0x7F800001,
            0xFFC00000, 0x3F800001]
    for (a, b) in zxi:
        for c in adds:
            r, f = ref_fma("f32", a, "f32", b, "f32", c, "te")
            emit("nanmat", "msf32_fma te %s %s %s -> %s %02x %s:nanmat" % (hx(a), hx(b), hx(c), hx(r), f, PROV))
            n += 1
    return n


def w_nanmat():
    n = 0
    nans = F32_QNAN + F32_SNAN
    fins = [0x00000000, 0x80000000, 0x3F800000, 0xBF800000, 0x7F800000, 0xFF800000,
            0x00000001, 0x7F7FFFFF]
    f64n = [0x7FF8000000000000, 0x7FF0000000000001, 0xFFF8000000000001]
    for o1 in nans:
        for o2 in fins:
            for nm, fn, ar in (("add", ref_addsub, 0), ("sub", ref_addsub, 1), ("mul", ref_mul, None),
                               ("div", ref_div, None)):
                args = (o1, o2) if (n % 2 == 0) else (o2, o1)
                if nm in ("add", "sub"):
                    r, f = fn("f32", args[0], "f32", args[1], ar, "te")
                else:
                    r, f = fn("f32", args[0], "f32", args[1], "te")
                emit("nanmat", "msf32_%s te %s %s -> %s %02x %s:nanmat" % (nm, hx(args[0]), hx(args[1]), hx(r), f, PROV))
                n += 1
    for o1 in f64n:  # cross-format payload conversion (f64 nan -> f32)
        for nm, fn, ar in (("add", ref_addsub, 0), ("mul", ref_mul, None)):
            if nm in ("add", "sub"):
                r, f = fn("f64", o1, "f32", 0x3F800000, ar, "te")
                emit("nanmat", "msf32_%s_f64_f32 te %s 3f800000 -> %s %02x %s:nanmat" % (nm, hx(o1), hx(r), f, PROV))
            else:
                r, f = fn("f64", o1, "f32", 0x3F800000, "te")
                emit("nanmat", "msf32_%s_f64_f32 te %s 3f800000 -> %s %02x %s:nanmat" % (nm, hx(o1), hx(r), f, PROV))
            n += 1
    # truncation-to-default: f64 qnan payload 1 narrows to f32 inf pattern
    r, f = ref_addsub("f64", 0x7FF0000000000001, "f32", 0x3F800000, 0, "te")
    emit("nanmat", "msf32_add_f64_f32 te 7ff0000000000001 3f800000 -> %s %02x %s:nanmat" % (hx(r), f, PROV))
    n += 1
    for a in F32_SNAN[:4]:  # sqrt/rint/next/logb NaN paths
        for nm, fn in (("sqrt", lambda: ref_sqrt("f32", a, "te")),
                       ("rint", lambda: ref_rint(a, "te", 0)),
                       ("nextup", lambda: ref_next(a, True)),
                       ("logb", lambda: ref_logb(a))):
            r, f = fn()
            op = {"sqrt": "msf32_sqrt", "rint": "msf32_round_to_integral_ties_to_even",
                  "nextup": "msf32_next_up", "logb": "msf32_log_b"}[nm]
            rm = "-" if nm in ("rint", "nextup", "logb") else "te"
            emit("nanmat", "%s %s %s -> %s %02x %s:nanmat" % (op, rm, hx(a), hx(r), f, PROV))
            n += 1
    return n


def w_zeros():
    n = 0
    zs = [0x00000000, 0x80000000]
    for a in zs:
        for b in zs + [0x3F800000, 0xBF800000, 0x7F800000, 0xFF800000, 0x00000001]:
            for rm in RMS:
                r, f = ref_addsub("f32", a, "f32", b, 0, rm)
                emit("zeros", "msf32_add %s %s %s -> %s %02x %s:zeros" % (rm, hx(a), hx(b), hx(r), f, PROV))
                r, f = ref_addsub("f32", a, "f32", b, 1, rm)
                emit("zeros", "msf32_sub %s %s %s -> %s %02x %s:zeros" % (rm, hx(a), hx(b), hx(r), f, PROV))
                n += 2
                r, f = ref_mul("f32", a, "f32", b, rm)
                emit("zeros", "msf32_mul %s %s %s -> %s %02x %s:zeros" % (rm, hx(a), hx(b), hx(r), f, PROV))
                r, f = ref_div("f32", a, "f32", b, rm)
                emit("zeros", "msf32_div %s %s %s -> %s %02x %s:zeros" % (rm, hx(a), hx(b), hx(r), f, PROV))
                n += 2
    for c in zs:
        for rm in RMS:
            r, f = ref_fma("f32", 0, "f32", 0x3F800000, "f32", c, rm)
            emit("zeros", "msf32_fma %s 0 3f800000 %s -> %s %02x %s:zeros" % (rm, hx(c), hx(r), f, PROV))
            n += 1
    return n


def w_remainder():
    n = 0
    divs = [0x00000000, 0x80000000, 0x3F800000, 0xBF800000, 0x40000000, 0x40490FDB,
            0x7F800000, 0xFF800000, 0x00000001, 0x80000001, 0x7F7FFFFF, 0x00800000,
            0x3FC00000, 0x42C80000, 0xC2C80000, 0x7FC00000, 0x7F800001]
    for a in F32_POOL[::2]:
        for b in divs:
            r, f = ref_remainder(a, b)
            emit("remainder", "msf32_remainder - %s %s -> %s %02x %s:remainder" % (hx(a), hx(b), hx(r), f, PROV))
            n += 1
    # exact-half boundaries and s>=25 early-out edge: |x|/|y| near 1/2 from both sides
    for a, b in [(0x3F800000, 0x40000000), (0x40000000, 0x3F800000), (0x00800000, 0x01000000),
                 (0x007FFFFF, 0x00FFFFFF), (0x7F7FFFFF, 0x00000001), (0x00000001, 0x7F7FFFFF),
                 (0x3F800000, 0x33800000), (0x33800000, 0x3F800000)]:
        r, f = ref_remainder(a, b)
        emit("remainder", "msf32_remainder - %s %s -> %s %02x %s:remainder" % (hx(a), hx(b), hx(r), f, PROV))
        n += 1
    return n


def w_next():
    n = 0
    for a in F32_POOL:
        for up, nm in ((True, "msf32_next_up"), (False, "msf32_next_down")):
            r, f = ref_next(a, up)
            emit("next", "%s - %s -> %s %02x %s:next" % (nm, hx(a), hx(r), f, PROV))
            n += 1
    return n


def w_scaleb():
    n = 0
    NPOOL = [0x0000000000000000, 0x8000000000000000, 0x3FF0000000000000, 0xBFF0000000000000,
             0x4000000000000000, 0xC000000000000000, 0x3FF8000000000000, 0xBFF4000000000000,
             0x4020000000000000, 0xC020000000000000, 0x4330000000000000, 0xC330000000000000,
             0x4340000000000000, 0xC340000000000000, 0x7FF0000000000000, 0xFFF0000000000000,
             0x7FF8000000000000, 0x7FF0000000000001, 0x0000000000000001, 0x8000000000000001,
             0x3F00000000000000, 0xBE00000000000000, 0x7FEFFFFFFFFFFFFF]
    for a in F32_POOL[::3]:
        for nb in NPOOL:
            for rm in RMS:
                r, f = ref_scaleb(a, nb, rm)
                emit("scaleb", "msf32_scale_b %s %s %s -> %s %02x %s:scaleb" % (rm, hx(a), hx(nb), hx(r), f, PROV))
                n += 1
    return n


def w_logb():
    n = 0
    for a in F32_POOL:
        r, f = ref_logb(a)
        emit("logb", "msf32_log_b - %s -> %s %02x %s:logb" % (hx(a), "%x" % r, f, PROV))
        n += 1
    return n


RINT_FORMS = [("ties_to_even", "te", 0), ("ties_to_away", "ta", 0), ("toward_zero", "tz", 0),
              ("toward_positive", "tp", 0), ("toward_negative", "tn", 0),
              ("exact_ties_to_even", "te", 1), ("exact_ties_to_away", "ta", 1),
              ("exact_toward_zero", "tz", 1), ("exact_toward_positive", "tp", 1),
              ("exact_toward_negative", "tn", 1)]
RINT_OPS = {"te": "msf32_round_to_integral_exact",
            "tz": "msf32_round_to_integral_exact", "tp": "msf32_round_to_integral_exact",
            "tn": "msf32_round_to_integral_exact", "ta": "msf32_round_to_integral_ties_to_away",
            "named-te": "msf32_round_to_integral_ties_to_even",
            "named-tz": "msf32_round_to_integral_toward_zero",
            "named-tp": "msf32_round_to_integral_toward_positive",
            "named-tn": "msf32_round_to_integral_toward_negative"}


def w_rint():
    n = 0
    vals = F32_POOL[::2] + [0x3F800001, 0xBF800001, 0x4B000001, 0xCB000001, 0x4EFFFFFF,
                            0xCEFFFFFF, 0x7F7FFFFF, 0x00800001]
    for a in vals:
        for suf, mode, ex in RINT_FORMS:
            if ex:
                op = "msf32_round_to_integral_exact"
                line_rm = mode
            elif suf == "ties_to_away":
                op = "msf32_round_to_integral_ties_to_away"
                line_rm = "-"
            else:
                op = "msf32_round_to_integral_%s" % suf
                line_rm = "-"
            r, f = ref_rint(a, mode, ex)
            emit("rint", "%s %s %s -> %s %02x %s:rint" % (op, line_rm, hx(a), hx(r), f, PROV))
            n += 1
    return n


def w_intconv():
    n = 0
    bounds = [0, 1, 2, 126, 127, 128, 129, 254, 255, 256, 257, 32766, 32767, 32768,
              32769, 65534, 65535, 65536, 2**24 - 1, 2**24, 2**24 + 1, 2**31 - 2, 2**31 - 1,
              2**31, 2**31 + 1, 2**32 - 1, 2**32, 2**53 - 1, 2**53, 2**53 + 1, 2**63 - 1,
              2**63, 2**64 - 1, 2**64, 2**100]
    fvals = set()
    for m in bounds:
        for v in (m, m + 0.5, m - 0.5 if m > 0 else -0.5, m + 0.25):
            for s in (1, -1):
                fvals.add(s * v)
    fvals.update([0.0, -0.0, 0.5, -0.5, 1.5, -1.5, 2.5, 127.5, -128.5, 255.5])
    specials = [0x00000000, 0x80000000, 0x7F800000, 0xFF800000, 0x7FC00000, 0xFFC00000,
                0x7F800001, 0x00000001, 0x80000001, 0x7F7FFFFF, 0xFF7FFFFF, 0x00800000]
    import struct
    tobits = []
    for v in sorted(fvals):
        try:
            tobits.append(struct.unpack("<I", struct.pack("<f", v))[0])
        except OverflowError:
            continue
    tobits = sorted(set(tobits + specials))
    forms = [("i8", 1, 8), ("u8", 0, 8), ("i16", 1, 16), ("u16", 0, 16),
             ("i32", 1, 32), ("u32", 0, 32), ("i64", 1, 64), ("u64", 0, 64)]
    for a in tobits:
        for tok, sg, w in forms:
            for suf, mode, ex in RINT_FORMS:
                op = "msf32_to_%s_%s" % (tok, suf)
                r, f = ref_to_int(a, sg, w, mode, ex)
                emit("toint", "%s - %s -> %s %02x %s:toint" % (op, hx(a), hx(r), f, PROV))
                n += 1
    mags = [0, 1, 2, 126, 127, 128, 129, 255, 256, 32767, 32768, 65535, 65536,
            2**24 - 1, 2**24, 2**24 + 1, 2**31 - 1, 2**31, 2**32 - 1, 2**32,
            2**53 - 1, 2**53, 2**53 + 1, 2**63 - 1, 2**63, 2**64 - 1]
    for tok, sg, w in [("i8", 1, 8), ("u8", 0, 8), ("i16", 1, 16), ("u16", 0, 16),
                       ("i32", 1, 32), ("u32", 0, 32), ("i64", 1, 64), ("u64", 0, 64)]:
        lo, hi = (-(1 << (w - 1)), (1 << (w - 1)) - 1) if sg else (0, (1 << w) - 1)
        vals = set()
        for m in mags:
            if sg:
                vals.update([m, -m])
            else:
                vals.add(m)
        vals = [v for v in vals if lo <= v <= hi]
        for v in vals:
            arg = hx(v, 8 if w == 8 else (16 if w == 16 else (32 if w == 32 else 64)))
            for rm in RMS:
                r, f = ref_from_int(v < 0 if sg else False, abs(v), rm)
                emit("fromint", "msf32_from_%s %s %s -> %s %02x %s:fromint" % (tok, rm, arg, hx(r), f, PROV))
                n += 1
    return n


CMP_A = [0x00000000, 0x80000000, 0x00000001, 0x80000001, 0x00800000, 0x80800000,
           0x3F800000, 0xBF800000, 0x40000000, 0xC0000000, 0x3F800001, 0x3F7FFFFF,
           0x7F7FFFFF, 0xFF7FFFFF, 0x7F800000, 0xFF800000,
           0x7FC00000, 0xFFC00000, 0x7FC00001, 0x7F800001, 0xFF800001, 0x7FFFFFFF,
           0x33800000, 0x4B7FFFFF]
def w_cmp():
    n = 0
    BH = F32_POOL[::6][:14]
    BX = F64_POOL[::6][:14]
    for pred in PREDS:
        for a in CMP_A:
            for b in BH:
                r, f = ref_cmp("f32", a, "f32", b, pred)
                emit("cmp", "msf32_compare_%s - %s %s -> %s %02x %s:cmp" % (pred, hx(a), hx(b), r, f, PROV))
                n += 1
        for a in CMP_A:
            for b in BX:
                r, f = ref_cmp("f32", a, "f64", b, pred)
                emit("cmp", "msf32_compare_%s_f64 - %s %s -> %s %02x %s:cmp" % (pred, hx(a), hx(b), r, f, PROV))
                n += 1
    return n


def w_total():
    n = 0
    skeleton_vals = [0xFFC12345, 0xFF800001, 0xFFC00000, 0xFF800000, 0xFF7FFFFF, 0xC0000000,
                     0x80000001, 0x80000000, 0x00000000, 0x00000001, 0x3F800000, 0x7F7FFFFF,
                     0x7F800000, 0x7F800001, 0x7FC00000, 0xFFC00001]
    for a in skeleton_vals:
        for b in skeleton_vals:
            for mag, nm in ((False, "msf32_total_order"), (True, "msf32_total_order_mag")):
                aa, bb = a, b
                if mag:
                    aa &= 0x7FFFFFFF
                    bb &= 0x7FFFFFFF
                r, kind = ref_total_order(aa, bb)
                if r == "PAYLOAD":
                    emit("payload", "%s - %s %s -> %s" % (nm, hx(aa), hx(bb), PROV))
                else:
                    emit("total", "%s - %s %s -> %s -- %s:total" % (nm, hx(aa), hx(bb), r, PROV))
                n += 1
    return n


def w_conv():
    n = 0
    for a in F32_POOL[::2]:
        for rm in RMS:
            # f32 -> f32 convert (same-format, nan quieting path)
            da = D("f32", a)
            from ref3 import nan_deliver as nd
            o, fl = nd("f32", [da], False)
            if o is not None:
                r, f = o, fl
            elif da.cls == "inf":
                r, f = (0xFF800000 if da.sign else 0x7F800000), 0
            elif da.cls == "zero":
                r, f = (0x80000000 if da.sign else 0), 0
            else:
                from ref3 import round_f32 as rf
                r, f = rf(da.sign, abs(da.val()), rm)
            emit("conv", "msf32_from_f32 %s %s -> %s %02x %s:conv" % (rm, hx(a), hx(r), f, PROV))
            n += 1
    for a in F64_POOL[::2]:
        for rm in RMS:
            da = D("f64", a)
            from ref3 import nan_deliver as nd, round_f32 as rf
            o, fl = nd("f32", [da], False)
            if o is not None:
                r, f = o, fl
            elif da.cls == "inf":
                r, f = (0xFF800000 if da.sign else 0x7F800000), 0
            elif da.cls == "zero":
                r, f = (0x80000000 if da.sign else 0), 0
            else:
                r, f = rf(da.sign, abs(da.val()), rm)
            emit("conv", "msf32_from_f64 %s %s -> %s %02x %s:conv" % (rm, hx(a), hx(r), f, PROV))
            n += 1
    return n


if __name__ == "__main__":
    total = 0
    for fn in (w_addsub, w_muldiv, w_sqrtfma, w_nanmat, w_zeros, w_remainder, w_next,
               w_scaleb, w_logb, w_rint, w_intconv, w_cmp, w_total, w_conv):
        c = fn()
        print("%s: %d" % (fn.__name__, c), file=sys.stderr)
        total += c
    for fam, ls in lines.items():
        if fam == "payload":
            continue
        with open(os.path.join(OUT, "p3-%s.vec" % fam), "w", newline="\n") as fh:
            fh.write("# verifier-w1f32 probe3 %s (independent exact-rational reference)\n" % fam)
            for ln in ls:
                fh.write(ln + "\n")
    with open(os.path.join(OUT, "p3-payload-pairs.txt"), "w", newline="\n") as fh:
        for ln in lines.get("payload", []):
            fh.write(ln + "\n")
    print("TOTAL: %d" % total, file=sys.stderr)

