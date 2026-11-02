#!/usr/bin/env python3
"""wv_cmpref.py - msf_cmp_finite vs exact rational comparison (own oracle).

Adversarial pairs: subnormal-vs-normal boundaries, exponent gaps >2000,
signed zeros, adjacent encodings, cross-format pairs. Exact values as
Fractions; expected = sign of (a-b), with -0 == +0.
"""
import subprocess
import sys
from fractions import Fraction

FMTS = {
    0: {"bits": 16, "t": 10, "w": 5, "bias": 15, "emin": -14},
    1: {"bits": 32, "t": 23, "w": 8, "bias": 127, "emin": -126},
    2: {"bits": 64, "t": 52, "w": 11, "bias": 1023, "emin": -1022},
}


def exact(fmt, bits):
    fp = FMTS[fmt]
    t = fp["t"]
    sign = (bits >> (fp["bits"] - 1)) & 1
    exp = (bits >> t) & ((1 << fp["w"]) - 1)
    frac = bits & ((1 << t) - 1)
    if exp == (1 << fp["w"]) - 1 or (exp == 0 and frac == 0 and False):
        raise ValueError("non-finite fed to oracle")
    if exp == 0:
        if frac == 0:
            return (sign, Fraction(0))
        return (sign, Fraction(frac, 1) * Fraction(2) ** (fp["emin"] - t))
    return (sign, Fraction(frac | (1 << t), 1) * Fraction(2) ** (exp - fp["bias"] - t))


def is_finite(fmt, bits):
    fp = FMTS[fmt]
    exp = (bits >> fp["t"]) & ((1 << fp["w"]) - 1)
    frac = bits & ((1 << fp["t"]) - 1)
    return not (exp == (1 << fp["w"]) - 1)


def enc(fmt, sign, exp, frac):
    return (sign << (FMTS[fmt]["bits"] - 1)) | (exp << FMTS[fmt]["t"]) | frac


def pairs():
    P = []
    # signed zeros all combos, all formats
    for f in (0, 1, 2):
        for a in (enc(f, 0, 0, 0), enc(f, 1, 0, 0)):
            for b in (enc(f, 0, 0, 0), enc(f, 1, 0, 0)):
                P.append((f, a, f, b))
    # largest subnormal vs smallest normal per format (both signs)
    for f in (0, 1, 2):
        t = FMTS[f]["t"]
        lo_sub = enc(f, 0, 0, 1)
        hi_sub = enc(f, 0, 0, (1 << t) - 1)
        lo_nor = enc(f, 0, 1, 0)
        lo_nor_n = enc(f, 1, 1, 0)
        hi_sub_n = enc(f, 1, 0, (1 << t) - 1)
        for (a, b) in [(hi_sub, lo_nor), (lo_nor, hi_sub), (lo_sub, lo_nor),
                       (hi_sub_n, lo_nor_n), (lo_nor, lo_nor_n), (hi_sub, hi_sub_n)]:
            P.append((f, a, f, b))
    # exponent gaps > 2000 (f64 min-subnormal vs max-normal etc.)
    f = 2
    tiny = enc(f, 0, 0, 1)
    huge = enc(f, 0, 2046, (1 << 52) - 1)
    huge_n = enc(f, 1, 2046, (1 << 52) - 1)
    tiny_n = enc(f, 1, 0, 1)
    zero = enc(f, 0, 0, 0)
    P += [(f, tiny, f, huge), (f, huge, f, tiny), (f, tiny_n, f, huge),
          (f, huge_n, f, tiny), (f, tiny, f, tiny_n), (f, huge, f, huge_n),
          (f, tiny, f, zero), (f, huge, f, zero)]
    # adjacent encodings across the range (f64): walk exponents
    for e in (0, 1, 2, 100, 1022, 1023, 1024, 2000, 2045, 2046):
        for fr in (0, 1, (1 << 52) - 1):
            a = enc(2, 0, e, fr)
            for db in (1, 2, 100):
                b = a + db
                if is_finite(2, b):
                    P.append((2, a, 2, b))
                    P.append((2, b, 2, a))
    # cross-format: same real value different widths (1.0, subnormal-ish, max)
    P += [(0, enc(0, 0, 15, 0), 1, enc(1, 0, 127, 0)),
          (1, enc(1, 0, 127, 0), 2, enc(2, 0, 1023, 0)),
          (0, enc(0, 0, 0, 1), 2, enc(2, 0, 0, 1)),
          (0, enc(0, 0, 30, 0x3ff), 1, enc(1, 0, 142, 0x7fffff)),
          (2, enc(2, 1, 1023, 0), 0, enc(0, 1, 15, 0))]
    # dedupe, keep finite only
    seen, out = set(), []
    for (fa, a, fb, b) in P:
        if not (is_finite(fa, a) and is_finite(fb, b)):
            continue
        if (fa, a, fb, b) not in seen:
            seen.add((fa, a, fb, b))
            out.append((fa, a, fb, b))
    return out


def main():
    drv, outfile = sys.argv[1], sys.argv[2]
    P = pairs()
    inp = "".join("%d %x %d %x\n" % q for q in P)
    proc = subprocess.run([drv], input=inp, capture_output=True, text=True)
    if proc.returncode != 0:
        print("CMP DRIVER FAILED\n%s" % proc.stderr)
        return 1
    lines = proc.stdout.splitlines()
    assert len(lines) == len(P), (len(lines), len(P))
    mm = 0
    first = []
    for (fa, a, fb, b), line in zip(P, lines):
        sa, va = exact(fa, a)
        sb, vb = exact(fb, b)
        if va == 0 and vb == 0:
            want = 0
        else:
            d = (va if sa == 0 else -va) - (vb if sb == 0 else -vb)
            want = 1 if d > 0 else (-1 if d < 0 else 0)
        got = int(line)
        if got != want:
            mm += 1
            if len(first) < 10:
                first.append("f%da=%x f%db=%x C=%d want=%d" % (fa, a, fb, b, got, want))
    rep = ["cmp pairs: %d, mismatches: %d" % (len(P), mm)] + ["  MM " + m for m in first]
    open(outfile, "w", encoding="utf-8").write("\n".join(rep) + "\n")
    print("\n".join(rep))
    return 0 if mm == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
