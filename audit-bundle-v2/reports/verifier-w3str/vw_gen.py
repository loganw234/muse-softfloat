#!/usr/bin/env python3
"""vw_gen.py - verifier-owned probe + fuzz vector generator (fresh code).
Uses vw_ref only. Usage:
  vw_gen.py adv OUTDIR       # directed adversaries (ties, grammar, corner, spec, buf)
  vw_gen.py fuzz FAM OUTFILE N SEED   # seeded random differentials, FAM in
                                      # from-dec|from-hex|to-dec|to-hex
Line shapes follow the ruled format (ledger/lead.md R5/R6, runner-verified).
"""
import sys
import os
import random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vw_ref import (ref_from_decimal, ref_from_hex, ref_to_decimal, ref_to_hex,
                    FMTS, PMIN, FL_INEXACT)

WIDTH = {"f16": 4, "f32": 8, "f64": 16}
OPW = {"f16": "msf16", "f32": "msf32", "f64": "msf64"}
RMS = ("te", "tz", "tp", "tn")


def bstr(b, fmt):
    return "%0*x" % (WIDTH[fmt], b)


def from_line(op, rm, s, fmt, fam, prov):
    b, fl, c = (ref_from_decimal(fmt, s, rm) if fam == "decimal"
                else ref_from_hex(fmt, s, rm))
    ins = "~" if s == "" else s
    return "%s %s IN=%s -> %s %02x C=%d %s" % (op, rm, ins,
                                              bstr(b, fmt), fl, c, prov)


def to_line(op, rm, bits, fmt, fam, spec, prov, buf=None):
    a = "%0*x" % (WIDTH[fmt], bits)
    if fam == "decimal":
        p, st, mn = spec
        o, L, fl = ref_to_decimal(fmt, bits, p, st, mn, rm)
        ss = "%d,%d,%d" % (p, st, mn)
    else:
        o, L, fl = ref_to_hex(fmt, bits, spec, rm)
        ss = "%d" % spec
    pre = " BUF=%d" % buf if buf is not None else ""
    outs = "~" if (buf is not None and L + 1 > buf) else o
    return "%s %s A=%s SPEC=%s%s -> OUT=%s LEN=%d %02x %s" % (
        op, rm, a, ss, pre, outs, L, fl, prov)


def adv_from_dec():
    L = []
    prov = "vw:adv-dec"
    # grammar adversaries incl consumed, whitespace-first, longest prefix
    # NOTE: space/tab-led inputs cannot be expressed in the space-token
    # vector format; they are covered by the vw_edge C harness instead.
    grams = ["", "+", "-", ".", "+.", "e5", "1e", "1e+",
             "1E-", "1.2.3", "0x1p1", "0X10", "1a", "1,5", "--1", "1ee5",
             "5e-", ".5.", "infi", "INFINITY", "infinit", "in", "nan(1)",
             "nan(0x1)", "nanx", "na", "snan", "SNAN", "-SNAN", "+snanx",
             "sna", "0e999999999", "-0.00e-999999999", "007", ".5", "5.",
             "1E5", "1e+005", "000.000", "123abc", "45.6.7e8", "+.5e+3",
             "-.0e-0", "00.5e0003", "9" * 21, "1" + "0" * 25,
             "0." + "0" * 30 + "1", "1" + "0" * 400, "1e-400",
             "9.99999999999999999999e999", "0.1", "-0.0", "+inf", "-INF",
             "+NaN", "-sNaN", "SNAN(1)", "infinityy", "INR", "sNAN "]
    for fmt in ("f16", "f32", "f64"):
        op = OPW[fmt] + "_from_decimal"
        for s in grams:
            for rm in (("te",) if len(s) > 12 else RMS):
                L.append(from_line(op, rm, s, fmt, "decimal", prov))
    # exact ties + one-ulp-off-tie, every dest x mode, normal + subnormal edge
    from fractions import Fraction
    for fmt in ("f16", "f32", "f64"):
        p, emax, emin = (FMTS[fmt]["p"], FMTS[fmt]["emax"], FMTS[fmt]["emin"])
        op = OPW[fmt] + "_from_decimal"
        ties = []
        for E in (2, -3, emax - 1, emin + 2):
            for m in (0, 1, 7, 123):
                ties.append(Fraction(2 * m + 1, 1) * Fraction(2) ** (E - p))
        # subnormal-boundary midpoint: between max subnormal and min normal
        ties.append(Fraction(2 ** (p - 1) * 2 - 1 + 0, 1) * Fraction(2) ** (emin - p))
        # 2^-x half-min-subnormal (tie to zero/even)
        ties.append(Fraction(2) ** (emin - p))
        for v in ties:
            for sgn in (1, -1):
                vv = v if sgn > 0 else -v
                s = frac_to_dec(vv)
                for rm in RMS:
                    L.append(from_line(op, rm, s if sgn > 0 else "-" + s,
                                       fmt, "decimal", "vw:ties"))
                # one-ulp-off-tie: nudge last decimal digit by +-1
                for ds in (s[:-1] + str((int(s[-1]) + 1) % 10),
                           s[:-1] + str((int(s[-1]) + 9) % 10)):
                    if ds and ds[-1] != s[-1]:
                        for rm in ("te", "tp"):
                            L.append(from_line(op, rm, ds if sgn > 0 else "-" + ds,
                                               fmt, "decimal", "vw:offtie"))
    # overflow directed-sign rows
    for fmt in ("f16", "f32", "f64"):
        op = OPW[fmt] + "_from_decimal"
        big = {"f16": "1e99", "f32": "1e99", "f64": "1e999"}[fmt]
        for sgn in ("", "+", "-"):
            for rm in RMS:
                L.append(from_line(op, rm, sgn + big, fmt, "decimal", "vw:ovf"))
    # beyond-H: exact-half at step1 even/odd kept, carry-9s, directed, corner
    bh = [
        ("4.5035996273704965e15", None),   # 17-digit control (within H)
        ("1.00000000000000000005e0", None),  # 21-digit, tail nonzero
        ("1.00000000000000000015e0", None),
        ("45035996273704965e-1", None),    # 17-digit tie-ish
        ("90071992547409935e-1", None),    # 17-digit, odd tie at f64
        ("90071992547409925e-1", None),    # 17-digit, even tie at f64
        ("7.41098468761869816265e-324", None),  # 21-digit min-subnormal zone
        ("2.47032822920623272001e-324", None),
        ("5960464477539062500004e-28", None),  # ruled corner: step2 exact tiny
        ("1" + "0" * 30 + "5", None),
        ("9" * 21, None),
        ("9" * 21 + "e5", None),
        ("1." + "0" * 20 + "5", None),
        ("3.1415926535897932385e0", None),
        ("2.22507385850720138309e-308", None),
        ("1.17549435082228750797e-38", None),
        ("6.10351562500000000001e-05", None),
        ("6.10351562499999999999e-05", None),
    ]
    for fmt in ("f16", "f32", "f64"):
        op = OPW[fmt] + "_from_decimal"
        for s, _ in bh:
            for sgn in ("", "-"):
                for rm in RMS:
                    L.append(from_line(op, rm, sgn + s, fmt, "decimal", "vw:beyondh"))
    return L


def frac_to_dec(fr):
    """Exact decimal string for Fraction fr (terminating)."""
    if fr < 0:
        return "-" + frac_to_dec(-fr)
    n, d = fr.numerator, fr.denominator
    k = 0
    while d % 2 == 0 or d % 5 == 0:
        if d % 2 == 0:
            d //= 2
            n *= 5
        else:
            d //= 5
            n *= 2
        k += 1
    assert d == 1
    s = str(n)
    if k == 0:
        return s
    if len(s) <= k:
        return "0." + "0" * (k - len(s)) + s
    return s[:-k] + "." + s[-k:]


def adv_from_hex():
    L = []
    grams = ["", " ", "0x", "0X", "0x.", "0x.8", "0x1.", "0x1.8", "0x1p",
             "0x1p+", "0xp1", "1.5", "1p1", "0x1.8p1", "0X1.8P+1", "0x.8p1",
             "0xabcdefp10", "0xABCDEFp-3", "0x0p0", "-0x0p+0", "0x0.0p0",
             "0x1.0000000000000001p0", "0x1.fffffffffffff8p1023",
             "0x0.0000000000001p-1022", "0x1.8p-1075", "0x1.8p-1076",
             "0x1.8p1023", "0x1.8p1024", "0x1.8p-1074", "0x2p0", "0xAp5",
             "0xg1p0", "0x1p1x", "0x1.2.3p4",
             "0x" + "f" * 40 + "p0", "0x0." + "0" * 40 + "1p0",
             "inf", "-INF", "snan", "+SNAN", "nan(1)", "0x1p999999999",
             "0x1p-999999999", "0x00.00p00", "+0xAb.CdP-7"]
    for fmt in ("f16", "f32", "f64"):
        op = OPW[fmt] + "_from_hex"
        for s in grams:
            for rm in (("te",) if len(s) > 14 else RMS):
                L.append(from_line(op, rm, s, fmt, "hex", "vw:adv-hex"))
    # hex ties: exact-half guard at rounding point, sticky variants
    from fractions import Fraction
    for fmt in ("f16", "f32", "f64"):
        p, emax, emin = (FMTS[fmt]["p"], FMTS[fmt]["emax"], FMTS[fmt]["emin"])
        op = OPW[fmt] + "_from_hex"
        for E in (0, -5, emin + 3, emax - 2):
            base = Fraction(2 ** (p - 1) + 1, 1) * Fraction(2) ** (E - p + 1)
            for v in (base, base + Fraction(2) ** (E - p - 60)):
                s = frac_to_hex(v)
                for rm in RMS:
                    L.append(from_line(op, rm, s, fmt, "hex", "vw:hexties"))
    return L


def frac_to_hex(fr):
    """Exact 0xH.HpE string for positive dyadic Fraction."""
    assert fr > 0
    n, d = fr.numerator, fr.denominator
    k = 0
    while d % 2 == 0:
        d //= 2
        k += 1
    assert d == 1
    import math
    bl = n.bit_length()
    E = bl - 1 - k
    # normalize: n has bl bits; want leading hex digit nonzero
    pad = (-bl) % 4
    h = "%x" % (n << pad)
    E -= pad
    if len(h) == 1:
        return "0x%sp%+d" % (h, E)
    return "0x%s.%sp%+d" % (h[0], h[1:], E - 4 * (len(h) - 1))


def adv_to_dec():
    L = []
    # spec matrix: floor case, FIXED shapes, zero shapes, huge sizing
    specs = [(2, 0, 5), (2, 0, 0), (5, 1, 0), (5, 0, 0), (0, 0, 0),
             (0, 1, 0), (1, 0, 0), (1, 1, 0), (9, 0, 0), (17, 0, 0),
             (20, 0, 0), (21, 0, 0), (25, 0, 0), (9, 1, 0), (3, 7, 0),
             (2, 1, 9), (100, 0, 0), (30, 1, 0)]
    vals = {"f16": [0x0000, 0x8000, 0x3C00, 0xBC00, 0x7C00, 0xFC00, 0x7E00,
                    0x7C01, 0x0400, 0x0001, 0x03FF, 0x7BFF, 0x3555, 0xC000,
                    0x8400, 0x0000],
            "f32": [0x00000000, 0x80000000, 0x3F800000, 0xBF800000, 0x7F800000,
                    0xFF800000, 0x7FC00000, 0x7F800001, 0x00800000, 0x00000001,
                    0x007FFFFF, 0x7F7FFFFF, 0x3F9DF3B2, 0xC0000000, 0x33800000],
            "f64": [0x0000000000000000, 0x8000000000000000, 0x3FF0000000000000,
                    0xBFF0000000000000, 0x7FF0000000000000, 0xFFF0000000000000,
                    0x7FF8000000000000, 0x7FF0000000000001, 0x0010000000000000,
                    0x0000000000000001, 0x000FFFFFFFFFFFFF, 0x7FEFFFFFFFFFFFFF,
                    0x3FF3BE76C8B43958, 0xC000000000000000, 0x3E00000000000000]}
    for fmt in ("f16", "f32", "f64"):
        op = OPW[fmt] + "_to_decimal"
        for a in vals[fmt]:
            for spec in specs:
                for rm in (RMS if spec[0] in (2, 9, 20) and a not in
                           (0x7C00, 0x7F800000, 0x7FF0000000000000) else ("te",)):
                    L.append(to_line(op, rm, a, fmt, "decimal", spec, "vw:spec"))
    # exact-fit / no-fit BUF sweep on a few shapes
    for fmt in ("f16", "f32", "f64"):
        op = OPW[fmt] + "_to_decimal"
        for a, spec in ((0x3C00 if fmt == "f16" else
                         0x3F800000 if fmt == "f32" else 0x3FF0000000000000,
                         (PMIN[fmt], 0, 0)),
                        (0x0001, (9, 0, 0))):
            o = to_line(op, "te", a, fmt, "decimal", spec, "vw:buf")
            L.append(o)
            # parse LEN back out for fit sweep
            ln = int([t for t in o.split() if t.startswith("LEN=")][0][4:])
            for buf in (0, 1, ln - 1 if ln > 1 else 0, ln, ln + 1, 64):
                L.append(to_line(op, "te", a, fmt, "decimal", spec, "vw:buf", buf=buf))
    # huge precision sizing (no materialization: BUF small)
    L.append(to_line("msf16_to_decimal", "te", 0x3C00, "f16", "decimal",
                     (1000000, 0, 0), "vw:bigprec", buf=64))
    L.append(to_line("msf64_to_hex", "te", 0x3FF0000000000000, "f64", "hex",
                     1000000, "vw:bigprec", buf=64))
    return L


def adv_to_hex():
    L = []
    precs = [-1, 0, 1, 2, 3, 5, 12, 13, 30]
    vals = {"f16": [0x0000, 0x8000, 0x3C00, 0x3FFF, 0x3C01, 0x0600, 0x03FF,
                    0x0400, 0x0001, 0x03FE, 0x7BFF, 0x7C00, 0xFC00, 0x7E00,
                    0x7C01, 0x3555, 0x3556],
            "f32": [0x00000000, 0x80000000, 0x3F800000, 0x3FFFFFFF, 0x3F800001,
                    0x00800000, 0x00400000, 0x00000001, 0x007FFFFF, 0x7F7FFFFF,
                    0x7F800000, 0xFF800000, 0x7FC00000, 0x7F800001, 0x3F9DF3B2],
            "f64": [0x0000000000000000, 0x8000000000000000, 0x3FF0000000000000,
                    0x3FFFFFFFFFFFFFFF, 0x3FF0000000000001, 0x0010000000000000,
                    0x0008000000000000, 0x0000000000000001, 0x000FFFFFFFFFFFFF,
                    0x7FEFFFFFFFFFFFFF, 0x7FF0000000000000, 0xFFF0000000000000,
                    0x7FF8000000000000, 0x7FF0000000000001, 0x3FF3BE76C8B43958]}
    for fmt in ("f16", "f32", "f64"):
        op = OPW[fmt] + "_to_hex"
        for a in vals[fmt]:
            for pr in precs:
                for rm in (RMS if pr in (0, 1, 2) else ("te",)):
                    L.append(to_line(op, rm, a, fmt, "hex", pr, "vw:hexspec"))
    for fmt in ("f16", "f32", "f64"):
        op = OPW[fmt] + "_to_hex"
        a = {"f16": 0x3C00, "f32": 0x3F800000,
             "f64": 0x3FF0000000000000}[fmt]
        o = to_line(op, "te", a, fmt, "hex", -1, "vw:buf")
        L.append(o)
        ln = int([t for t in o.split() if t.startswith("LEN=")][0][4:])
        for buf in (0, 1, ln - 1, ln, ln + 1):
            L.append(to_line(op, "te", a, fmt, "hex", -1, "vw:buf", buf=buf))
    return L


def fuzz(fam, n, seed):
    rnd = random.Random(seed)
    L = []
    if fam == "from-dec":
        for i in range(n):
            fmt = rnd.choice(["f16", "f32", "f64"])
            rm = rnd.choice(RMS)
            op = OPW[fmt] + "_from_decimal"
            s = rnd_dec(rnd)
            L.append(from_line(op, rm, s, fmt, "decimal", "vw:fuzz-dec"))
    elif fam == "from-hex":
        for i in range(n):
            fmt = rnd.choice(["f16", "f32", "f64"])
            rm = rnd.choice(RMS)
            op = OPW[fmt] + "_from_hex"
            s = rnd_hex(rnd)
            L.append(from_line(op, rm, s, fmt, "hex", "vw:fuzz-hex"))
    elif fam == "to-dec":
        for i in range(n):
            fmt = rnd.choice(["f16", "f32", "f64"])
            rm = rnd.choice(RMS)
            op = OPW[fmt] + "_to_decimal"
            a = rnd_bits(rnd, fmt)
            spec = (rnd.choice([0, 1, 2, 5, 9, 17, 20, 21, 30]),
                    rnd.choice([0, 1]), rnd.choice([0, 0, 0, 5, 9]))
            L.append(to_line(op, rm, a, fmt, "decimal", spec, "vw:fuzz-todec"))
    elif fam == "to-hex":
        for i in range(n):
            fmt = rnd.choice(["f16", "f32", "f64"])
            rm = rnd.choice(RMS)
            op = OPW[fmt] + "_to_hex"
            a = rnd_bits(rnd, fmt)
            spec = rnd.choice([-1, -1, 0, 1, 2, 3, 5, 13, 30])
            L.append(to_line(op, rm, a, fmt, "hex", spec, "vw:fuzz-tohex"))
    return L


def rnd_dec(rnd):
    r = rnd.random()
    sgn = rnd.choice(["", "", "", "+", "-"])
    if r < 0.04:
        return sgn + rnd.choice(["inf", "infinity", "nan", "sNaN", "infi",
                                 "nan(1)", "0x1p1", ".", "e5", "1e", ""])
    nd = rnd.choice([1, 2, 3, 5, 9, 15, 19, 20, 21, 22, 25, 30, 40])
    digs = "".join(rnd.choice("0123456789") for _ in range(nd)).lstrip("0") or "0"
    if rnd.random() < 0.5 and len(digs) > 1:
        at = rnd.randrange(len(digs))
        digs = digs[:at] + "." + digs[at:]
    else:
        if rnd.random() < 0.4:
            digs += "." + "".join(rnd.choice("0123456789")
                                  for _ in range(rnd.randrange(4)))
    if rnd.random() < 0.45:
        # extreme exponents are rare (they dominate runtime via 10**E bignums
        # and are covered by directed overflow/underflow sets anyway)
        big = rnd.random() < 0.02
        digs += rnd.choice(["e", "E"]) + rnd.choice(["", "+", "-"]) + str(
            rnd.choice([999, 1000000, 400]) if big else
            rnd.choice([0, 1, 5, 38, 300, 308]))
    return sgn + digs


def rnd_hex(rnd):
    r = rnd.random()
    sgn = rnd.choice(["", "", "", "+", "-"])
    if r < 0.04:
        return sgn + rnd.choice(["inf", "nan", "snan", "0x", "0x1.8", "1.5",
                                 "0x1p", ""])
    nd = rnd.randrange(1, 14)
    digs = "".join(rnd.choice("0123456789abcdefABCDEF") for _ in range(nd))
    if rnd.random() < 0.6:
        at = rnd.randrange(len(digs) + 1)
        digs = digs[:at] + "." + digs[at:]
    if rnd.random() < 0.02:
        p = rnd.choice([999999, -999999])
    else:
        p = rnd.choice([0, 1, 5, -5, 100, -1074, 1023, -14])
    return sgn + rnd.choice(["0x", "0X"]) + digs + rnd.choice(["p", "P"]) + (
        ("+" if rnd.random() < 0.3 and p >= 0 else "") + str(p))


def rnd_bits(rnd, fmt):
    r = rnd.random()
    if fmt == "f16":
        if r < 0.12:
            return rnd.choice([0x0000, 0x8000, 0x7C00, 0xFC00, 0x7E00,
                               0xFE00, 0x7C01, 0x0001, 0x03FF, 0x7BFF])
        return rnd.randrange(0x10000)
    if fmt == "f32":
        if r < 0.12:
            return rnd.choice([0x00000000, 0x80000000, 0x7F800000, 0xFF800000,
                               0x7FC00000, 0x7F800001, 0x00000001, 0x007FFFFF,
                               0x7F7FFFFF])
        return rnd.randrange(2 ** 32)
    if r < 0.12:
        return rnd.choice([0x0000000000000000, 0x8000000000000000,
                           0x7FF0000000000000, 0xFFF0000000000000,
                           0x7FF8000000000000, 0x7FF0000000000001,
                           0x0000000000000001, 0x000FFFFFFFFFFFFF,
                           0x7FEFFFFFFFFFFFFF])
    return rnd.randrange(2 ** 64)


def main(argv):
    if argv[1] == "adv":
        outdir = argv[2]
        os.makedirs(outdir, exist_ok=True)
        sets = {"vw-adv-dec.vec": adv_from_dec(),
                "vw-adv-hex.vec": adv_from_hex(),
                "vw-adv-todec.vec": adv_to_dec(),
                "vw-adv-tohex.vec": adv_to_hex()}
        tot = 0
        for fn, lines in sets.items():
            with open(os.path.join(outdir, fn), "w", newline="\n") as f:
                f.write("# generated by vw_gen.py adv - do not edit\n")
                for ln in lines:
                    f.write(ln + "\n")
            tot += len(lines)
            print("%s: %d" % (fn, len(lines)))
        print("adv total %d" % tot)
    elif argv[1] == "fuzz":
        fam, out, n, seed = argv[2], argv[3], int(argv[4]), int(argv[5])
        lines = fuzz(fam, n, seed)
        with open(out, "w", newline="\n") as f:
            f.write("# generated by vw_gen.py fuzz %s seed %d - do not edit\n" % (fam, seed))
            for ln in lines:
                f.write(ln + "\n")
        print("%s: %d" % (fam, len(lines)))


if __name__ == "__main__":
    main(sys.argv)
