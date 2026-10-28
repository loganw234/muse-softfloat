#!/usr/bin/env python3
"""Committed directed vectors for rSqrt (SF-2 Step 2a).

Expected values are decided by MPFR through the Step 0b
operation recipe in tests/alg_decider.c (build it first; path
from MSF_ALG_DECIDER or build/alg/alg_decider.exe) and
cross-decided for every input and every mode by the exact
integer decider in this file (midpoint compares by exact
rational squaring - a different code path from the C
kernel). Generation REFUSES on any disagreement, including
on specials, whose expectations are computed here from the
settled 9.2.1 table (ledger/parcel-w5alg1.md design entry)
and never sourced from MPFR - the rSqrt(-0) cell in
particular, where executed MPFR is known to disagree with
the clause cell.

The fifth attribute (ta) is printed by the decider equal to
te (raw MPFR RNDNA is prohibited and unused); the exact
decider decides ta independently from the midpoint compare,
so the equality - exact ties are unattainable for rSqrt -
is verified per case and aborts generation if a true tie
is ever constructed.

Input families per format (~240 inputs, five modes each,
~1,200 lines): specials (signed zeros and infinities,
quiet/signaling NaN payload samples, negative finite
samples); directed (perfect-square lattice - the exact
results - with neighbours, powers of two across the
exponent range, binade edges: smallest/largest subnormal,
smallest normal, largest finite, one); ties
(midpoint-adjacent constructions - encodings nearest the
reciprocal square of sampled destination midpoints, the
hardest-to-round inputs rSqrt admits, since exact ties are
unattainable); seeded (seeded finite-positive encodings).

Usage: gen_vectors_alg.py OUTDIR   (writes alg-f16.vec,
alg-f32.vec, alg-f64.vec; byte-identical regeneration)
"""
import os
import random
import subprocess
import sys
from fractions import Fraction
from math import isqrt

FMTS = {
    "f16": (16, 5),
    "f32": (32, 8),
    "f64": (64, 11),
}
RMS = ("te", "tz", "tp", "tn", "ta")
INVALID = 0x01
DIVZERO = 0x02
INEXACT = 0x10
TARGET_INPUTS = 240


def params(fmt):
    bits, w = FMTS[fmt]
    t = bits - 1 - w
    bias = (1 << (w - 1)) - 1
    return {
        "bits": bits, "w": w, "t": t, "p": t + 1,
        "bias": bias, "emin": 1 - bias, "emax": bias,
        "emaxf": (1 << w) - 1,
        "sign": 1 << (bits - 1),
        "fracmask": (1 << t) - 1,
        "qbit": 1 << (t - 1),
        "inf": ((1 << w) - 1) << t,
        "one": bias << t,
        "maxfin": ((((1 << w) - 2) << t) | ((1 << t) - 1)),
    }


def fields(fmt, x):
    q = params(fmt)
    return ((x >> (q["bits"] - 1)) & 1,
            (x >> q["t"]) & q["emaxf"],
            x & q["fracmask"], q)


def encode_value(fmt, v: Fraction):
    """Exact encoding of a dyadic rational that fits, or None.
    Used only to BUILD directed inputs."""
    q = params(fmt)
    if v == 0:
        return 0
    sign = 1 if v < 0 else 0
    av = abs(v)
    m, d = av.numerator, av.denominator
    if d & (d - 1):
        return None
    e = -(d.bit_length() - 1)
    bl = m.bit_length()
    unbiased = e + bl - 1
    emin = q["emin"]
    if unbiased >= emin:
        if bl > q["p"]:
            return None
        frac = (m << (q["p"] - bl)) - (1 << (q["p"] - 1))
        ef = unbiased + q["bias"]
        if ef >= q["emaxf"]:
            return None
        return (sign << (q["bits"] - 1)) | (ef << q["t"]) | frac
    shift = emin - q["t"] - e
    if shift < 0:
        return None
    frac = m << shift
    if frac >= (1 << q["t"]) or frac == 0:
        return None
    return (sign << (q["bits"] - 1)) | frac


def floor_encode(fmt, v: Fraction):
    """Bits of the largest positive encoding <= v (v > 0)."""
    q = params(fmt)
    maxfin = (Fraction(2) - Fraction(2) ** (1 - q["p"])) * Fraction(2) ** q["emax"]
    if v >= maxfin:
        return q["maxfin"]
    e = v.numerator.bit_length() - v.denominator.bit_length()
    while Fraction(2) ** (e + 1) <= v:
        e += 1
    while Fraction(2) ** e > v:
        e -= 1
    if e >= q["emin"]:
        ulp = Fraction(2) ** (e - q["t"])
        frac = int(v / ulp) - (1 << q["t"])
        return ((e + q["bias"]) << q["t"]) | frac
    ulp = Fraction(2) ** (q["emin"] - q["t"])
    return int(v / ulp)


def neighbours(fmt, x, n=1):
    q = params(fmt)
    mask = (1 << q["bits"]) - 1
    return [y for y in (x + d for d in range(-n, n + 1)) if 0 <= y <= mask]


# --- exact decider (independent of the C kernel and MPFR) ---

def exact_special(fmt, x):
    """Settled-table expectation x5 modes, or None if regular."""
    sign, e, frac, q = fields(fmt, x)
    sbit = sign << (q["bits"] - 1)
    if e == q["emaxf"]:
        if frac == 0:
            if sign:
                return [(q["inf"] | q["qbit"], INVALID)] * 5
            return [(0, 0)] * 5
        r = x | q["qbit"]
        return [(r, 0 if frac & q["qbit"] else INVALID)] * 5
    if e == 0 and frac == 0:
        return [(sbit | q["inf"], DIVZERO)] * 5
    if sign:
        return [(q["inf"] | q["qbit"], INVALID)] * 5
    return None


def exact_decide(fmt, x):
    sp = exact_special(fmt, x)
    if sp is not None:
        return sp
    q = params(fmt)
    _, e, frac, _ = fields(fmt, x)
    if e == 0:
        sig, ex = frac, q["emin"] - q["t"]
    else:
        sig, ex = frac | (1 << q["t"]), e - q["bias"] - q["t"]
    xv = Fraction(sig) * Fraction(2) ** ex
    # Decide y with y^2 = f, by exact rational squaring.
    f = 1 / xv
    p, t = q["p"], q["t"]
    eout = (f.numerator.bit_length() - f.denominator.bit_length()) // 2
    while Fraction(2) ** (2 * (eout + 1)) <= f:
        eout += 1
    while Fraction(2) ** (2 * eout) > f:
        eout -= 1
    assert q["emin"] <= eout <= q["emax"], (fmt, x, eout)
    ulp2 = Fraction(2) ** (2 * (eout - (p - 1)))
    ratio = f / ulp2
    n = isqrt(ratio.numerator // ratio.denominator)
    exact = Fraction(n * n) * ulp2 == f
    # 4f vs (2n+1)^2 * ulp2 decides against the midpoint.
    cmp4 = 4 * f - Fraction((2 * n + 1) ** 2) * ulp2
    out = []
    for rm in RMS:
        if exact:
            c = n
        elif rm in ("tz", "tn"):
            c = n
        elif rm == "tp":
            c = n + 1
        elif cmp4 > 0:
            c = n + 1
        elif cmp4 < 0:
            c = n
        elif rm == "ta":
            c = n + 1
        else:  # te tie
            c = n if n % 2 == 0 else n + 1
        cc, ee = c, eout
        if cc == (1 << p):
            cc, ee = 1 << (p - 1), ee + 1
        bits = ((ee + q["bias"]) << t) | (cc - (1 << t))
        out.append((bits, 0 if exact else INEXACT))
    return out


# --- directed input families ---

def fam_specials(fmt):
    q = params(fmt)
    s = q["sign"]
    payloads = [1, 2, 3, (1 << (q["t"] - 1)) - 1, 1 << (q["t"] - 2)]
    out = [0, s, q["inf"], q["inf"] | s, q["inf"] | q["qbit"]]
    for pl in payloads:
        out += [q["inf"] | q["qbit"] | pl, q["inf"] | q["qbit"] | pl | s,
                q["inf"] | pl, q["inf"] | pl | s]
    out += [s | q["one"], s | 1, s | (1 << q["t"]), s | q["maxfin"]]
    return out


def fam_directed(fmt):
    q = params(fmt)
    out = set()
    # binade edges
    minnorm = 1 << q["t"]
    for x in list(range(1, 7)) + [q["one"], minnorm, (1 << q["t"]) - 1,
                                  q["maxfin"]]:
        out.update(neighbours(fmt, x, 2))
    # powers of two across the exponent range
    exps = [q["emin"], q["emin"] + 1, -64, -32, -16, -8, -4, -2, -1, 0,
            1, 2, 4, 8, 16, 32, 64, q["emax"] - 1, q["emax"]]
    for e in exps:
        if q["emin"] <= e <= q["emax"]:
            x = encode_value(fmt, Fraction(2) ** e)
            if x is not None:
                out.update(neighbours(fmt, x, 1))
    # smallest-subnormal class inputs (largest results)
    for f_ in (1, 2, 3, 5, 7, 11, 101):
        if f_ < (1 << q["t"]):
            out.add(f_)
    # perfect-square lattice: x a square => exact results
    for k in (1, 2, 3, 5, 7, 16, 25, 49):
        for j in (-3, -1, 0, 1):
            v = Fraction(k * k) * Fraction(2) ** (2 * j)
            x = encode_value(fmt, v)
            if x is not None:
                out.add(x)
                out.update(neighbours(fmt, x, 1))
    # scaled squares with odd factors at binade starts
    for k in (3, 5, 11, 101, 1001):
        for e in (-13, 0, 17):
            v = Fraction(k * k) * Fraction(2) ** e
            x = encode_value(fmt, v)
            if x is not None:
                out.add(x)
    return sorted(out)


def fam_ties(fmt):
    """Midpoint-adjacent: encodings nearest 1/mid^2 for sampled
    destination midpoints mid (odd (p+1)-bit significands)."""
    q = params(fmt)
    p, t = q["p"], q["t"]
    out = set()
    ms = [(1 << p) + 1, (1 << p) + 3, (1 << (p + 1)) - 1,
          (1 << (p + 1)) - 3, ((3 << (p - 1)) | 1)]
    exps = [-100, -17, -1, 0, 1, 23]
    exps = [e for e in exps if q["emin"] <= e <= q["emax"]]
    if fmt == "f16":
        exps = [-14, -7, -1, 0, 1, 12]
    for e in exps:
        for m in ms:
            mid = Fraction(m) * Fraction(2) ** (e - p)
            x0 = 1 / (mid * mid)
            b = floor_encode(fmt, x0)
            out.update(neighbours(fmt, b, 1))
    return sorted(out)


def fam_seeded(fmt, n, seed):
    q = params(fmt)
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        x = rng.getrandbits(q["bits"]) & ~q["sign"]
        _, e, _, _ = fields(fmt, x)
        if e == q["emaxf"]:
            continue
        out.append(x)
    return out


def build_inputs(fmt):
    fams = [("specials", fam_specials(fmt)),
            ("directed", fam_directed(fmt)),
            ("ties", fam_ties(fmt))]
    have = len({x for _, xs in fams for x in xs})
    fams.append(("seeded", fam_seeded(
        fmt, max(0, TARGET_INPUTS - have), 20261028 + int(fmt[1:]))))
    seen, out = set(), []
    for fam, xs in fams:
        for x in xs:
            if x not in seen:
                seen.add(x)
                out.append((fam, x))
    return out


def opname(fmt):
    return f"msf{fmt[1:]}_r_sqrt"


def main():
    outdir = sys.argv[1]
    exe = os.environ.get(
        "MSF_ALG_DECIDER",
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "build", "alg", "alg_decider.exe"))
    if not os.path.exists(exe):
        print(f"decider not found: {exe} (set MSF_ALG_DECIDER)",
              file=sys.stderr)
        return 2
    jobs = []
    for fmt in FMTS:
        for fam, x in build_inputs(fmt):
            jobs.append((fmt, fam, x))
    inp = "".join(f"{opname(fmt)} {x:x}\n" for fmt, _, x in jobs)
    proc = subprocess.run([exe, "decide"], input=inp,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout[-2000:])
        sys.stderr.write(proc.stderr[-2000:])
        print("decider failed", file=sys.stderr)
        return 1
    decided = {}
    for line in proc.stdout.splitlines():
        tk = line.split()
        if len(tk) == 12:
            decided[(tk[0], tk[1])] = [
                (int(tk[2 + 2 * i], 16), int(tk[3 + 2 * i], 16))
                for i in range(5)]
    if len(decided) != len(jobs):
        print(f"decider returned {len(decided)} of {len(jobs)}",
              file=sys.stderr)
        return 1
    files = {fmt: [] for fmt in FMTS}
    counts = {}
    for fmt, fam, x in jobs:
        op = opname(fmt)
        exp = decided[(op, f"{x:x}")]
        mine = exact_decide(fmt, x)
        if mine != exp:
            print(f"DISAGREE {op} {x:x}: exact-py {mine} decider {exp}",
                  file=sys.stderr)
            return 1
        counts[fam] = counts.get(fam, 0) + 5
        for rm, (rb, rf) in zip(RMS, exp):
            files[fmt].append(
                f"{op} {rm} {x:x} -> {rb:x} {rf:02x} mpfr-alg:{fam}")
    os.makedirs(outdir, exist_ok=True)
    total = 0
    for fmt in FMTS:
        path = os.path.join(outdir, f"alg-{fmt}.vec")
        with open(path, "w", newline="\n", encoding="utf-8") as fh:
            fh.write("# generated by tests/gen_vectors_alg.py"
                     " - do not edit (regenerate)\n")
            fh.write("# expectations: MPFR Step 0b operation recipe"
                     " (tests/alg_decider.c), cross-decided per case\n")
            fh.write("# by the generator's exact integer decider;"
                     " specials table-decided (rSqrt(-0) never MPFR)\n")
            for line in files[fmt]:
                fh.write(line + "\n")
        total += len(files[fmt])
        print(f"wrote {path}: {len(files[fmt])} lines")
    print(f"total {total} lines; by family {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
