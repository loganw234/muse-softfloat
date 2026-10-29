#!/usr/bin/env python3
"""Committed directed vectors for exp2/exp2m1 (SF-2 Step 3a)
and log2/log2p1 (Step 3b extension; log families per
ledger/parcel-w5log2.md Sec. 7, settled table restated
in expected_table_log; log tie set is empty by proof
there, ta still independently decided).

Expected values are decided by the adaptive-precision MPFR
bracket decider in tests/explog_decider.c, driven through
the `decide` mode of tests/explog_exhaustive.c (build it
first; path from MSF_EXPLOG_DECIDER or
build/explog/explog_exhaustive.exe) in all FIVE modes -
ties exist for these functions (integer inputs), so `ta`
lines are independently decided, never relabeled.
Provenance family: mpfr-explog:* (one tag per input family).

Specials and integer inputs are ALSO computed here from
first principles (the Clause 9.2 table of
ledger/parcel-w5exp2.md Sec. 2 and the exact/tie table of
its Sec. 3, rounded by an exact Fraction rounder written
for this generator) and generation REFUSES if the C
decider disagrees on any of them - the two implementations
cross-check, including the tie cells exp2(emin-p) and
exp2m1(+- (p+1)) under ties-to-away.

Input families per format/function: specials (zeros,
infinities, quiet/signaling NaN payload samples), integer
anchors (every exact/tie cell of the design table with
+-1 ulp neighbours), cut thresholds (each kernel
threshold value at -3..+3 ulp), a dyadic lattice, tiny /
subnormal inputs, the exp2m1 saturation strip ladder, the
exp2 subnormal-result and overflow strips, hardest
excerpts (binary64: the spike-measured plain-class maxima
patterns of scratch/sf2-explog/report.md Sec. 2.1, inputs
only; every value re-decided here), and a seeded class
sweep.

Usage: gen_vectors_explog.py OUTDIR (writes
explog-f16.vec, explog-f32.vec, explog-f64.vec;
byte-identical regeneration)
"""
import os
import random
import subprocess
import sys
from fractions import Fraction

FMTS = {
    "f16": (16, 5),
    "f32": (32, 8),
    "f64": (64, 11),
}
FNS = ("exp2", "exp2m1", "log2", "log2p1")
RMS = ("te", "tz", "tp", "tn", "ta")
INVALID = 0x01
DIVBYZERO = 0x02
OVERFLOW = 0x04
UNDERFLOW = 0x08
INEXACT = 0x10


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
    }


def fields(fmt, x):
    q = params(fmt)
    return ((x >> (q["bits"] - 1)) & 1,
            (x >> q["t"]) & q["emaxf"],
            x & q["fracmask"], q)


def encode_value(fmt, v: Fraction):
    """Exact encoding of a dyadic rational that fits, or
    None. Used only to BUILD directed inputs."""
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
    if unbiased >= q["emin"]:
        if bl > q["p"]:
            return None
        frac = (m << (q["p"] - bl)) - (1 << (q["p"] - 1))
        ef = unbiased + q["bias"]
        if ef >= q["emaxf"]:
            return None
        return (sign << (q["bits"] - 1)) | (ef << q["t"]) | frac
    shift = q["emin"] - q["t"] - e
    if shift < 0:
        return None
    frac = m << shift
    if frac >= (1 << q["t"]) or frac == 0:
        return None
    return (sign << (q["bits"] - 1)) | frac


def decode_value(fmt, x):
    """Exact Fraction value of a finite encoding, or None."""
    sign, e, frac, q = fields(fmt, x)
    if e == q["emaxf"]:
        return None
    if e == 0:
        v = Fraction(frac) * Fraction(2) ** (q["emin"] - q["t"])
    else:
        v = Fraction(frac | (1 << q["t"])) * Fraction(2) ** (e - q["bias"] - q["t"])
    return -v if sign else v


def neighbours(fmt, x, n=3):
    q = params(fmt)
    mask = (1 << q["bits"]) - 1
    return [x + d for d in range(-n, n + 1) if 0 <= x + d <= mask]


def floor_log2(fr: Fraction):
    e = fr.numerator.bit_length() - fr.denominator.bit_length()
    while Fraction(2) ** e > fr:
        e -= 1
    while Fraction(2) ** (e + 1) <= fr:
        e += 1
    return e


def round_grid_mag(a: Fraction, g, sign, rm):
    """Round positive Fraction a on the grid of spacing 2^g:
    returns (integer count, inexact)."""
    sc = a / Fraction(2) ** g
    iv = sc.numerator // sc.denominator
    fr = sc - iv
    inc = 0
    if rm == "te":
        inc = 1 if (fr > Fraction(1, 2) or (fr == Fraction(1, 2) and iv % 2 == 1)) else 0
    elif rm == "ta":
        inc = 1 if fr >= Fraction(1, 2) else 0
    elif rm == "tz":
        inc = 0
    elif rm == "tp":
        inc = 1 if (not sign and fr > 0) else 0
    elif rm == "tn":
        inc = 1 if (sign and fr > 0) else 0
    return iv + inc, fr > 0


def round_fraction(fmt, v: Fraction, rm):
    """First-principles round of an exact Fraction to the
    format: (bits, flags). Mirror-in-math of the C decider
    grid narrow, independently written."""
    q = params(fmt)
    sign = 1 if v < 0 else 0
    sbit = sign << (q["bits"] - 1)
    a = abs(v)
    if a == 0:
        return sbit, 0
    e = floor_log2(a)
    g = e - (q["p"] - 1) if e >= q["emin"] else q["emin"] - (q["p"] - 1)
    iu, inexact = round_grid_mag(a, g, sign, rm)
    tiny = False
    if e < q["emin"]:
        iuu, _ = round_grid_mag(a, e - (q["p"] - 1), sign, rm)
        ru = Fraction(iuu) * Fraction(2) ** (e - (q["p"] - 1))
        tiny = ru < Fraction(2) ** q["emin"]
    if iu >= (1 << q["p"]):
        iu >>= 1
        g += 1
    if iu != 0:
        top = g + iu.bit_length() - 1
        if top > q["emax"]:
            to_inf = rm in ("te", "ta") or (rm == "tp" and not sign) or (rm == "tn" and sign)
            if to_inf:
                return sbit | q["inf"], OVERFLOW | INEXACT
            return (sbit | ((q["emaxf"] - 1) << q["t"]) | q["fracmask"],
                    OVERFLOW | INEXACT)
    if iu >= (1 << (q["p"] - 1)):
        eunb = g + (q["p"] - 1)
        bits = sbit | ((eunb + q["bias"]) << q["t"]) | (iu - (1 << (q["p"] - 1)))
    else:
        bits = sbit | iu
    fl = (INEXACT if inexact else 0) | (UNDERFLOW if (inexact and tiny) else 0)
    return bits, fl


def expected_table(fmt, fn, x):
    """Settled-table expectation ((bits,flags) x 5 modes) for
    specials and integer inputs, or None. Independent
    Python restatement of ledger Secs. 2-3."""
    sign, e, frac, q = fields(fmt, x)
    sbit = sign << (q["bits"] - 1)
    is_m1 = fn == "exp2m1"
    if e == q["emaxf"]:
        if frac == 0:
            if not sign:
                r = q["inf"]
            elif is_m1:
                r = sbit | q["one"]
            else:
                r = 0
            return [(r, 0)] * 5
        r = x | q["qbit"]
        fl = 0 if frac & q["qbit"] else INVALID
        return [(r, fl)] * 5
    v = decode_value(fmt, x)
    if v == 0:
        r = sbit if is_m1 else q["one"]
        return [(r, 0)] * 5
    if v.denominator == 1:
        n = int(v)
        # Huge integers (every large-magnitude encoding is
        # one): never form 2^n; the proxy exact values round
        # identically (overflow / u/2 / saturation bands).
        if n > q["emax"] + 65:
            exact = Fraction(2) ** (q["emax"] + 2)
            return [round_fraction(fmt, exact, rm) for rm in RMS]
        if n < -4200:
            if is_m1:
                exact = -(1 - Fraction(2) ** -(q["p"] + 8))
            else:
                exact = Fraction(2) ** (q["emin"] - q["p"] - 2)
            return [round_fraction(fmt, exact, rm) for rm in RMS]
        exact = Fraction(2) ** n if not is_m1 else Fraction(2) ** n - 1
        return [round_fraction(fmt, exact, rm) for rm in RMS]
    return None


def expected_table_log(fmt, fn, x):
    """Settled-table expectation for log2/log2p1 specials,
    domain/pole cells, and power-of-two exacts, or None.
    Independent restatement of ledger/parcel-w5log2.md
    Secs. 2-3 (tie set empty: powers deliver the integer
    k exactly, everything else here is a table cell)."""
    sign, e, frac, q = fields(fmt, x)
    sbit = sign << (q["bits"] - 1)
    neginf = q["sign"] | q["inf"]
    defqnan = q["inf"] | q["qbit"]
    is_p1 = fn == "log2p1"
    if e == q["emaxf"]:
        if frac == 0:
            if sign:
                return [(defqnan, INVALID)] * 5
            return [(q["inf"], 0)] * 5
        r = x | q["qbit"]
        fl = 0 if frac & q["qbit"] else INVALID
        return [(r, fl)] * 5
    v = decode_value(fmt, x)
    if v == 0:
        if is_p1:
            return [(sbit, 0)] * 5
        return [(neginf, DIVBYZERO)] * 5
    if not is_p1 and v < 0:
        return [(defqnan, INVALID)] * 5
    if is_p1:
        if v < -1:
            return [(defqnan, INVALID)] * 5
        if v == -1:
            return [(neginf, DIVBYZERO)] * 5
    w = v if not is_p1 else 1 + v
    # w > 0 dyadic: power of two iff numerator is one.
    n, d = w.numerator, w.denominator
    if n & (n - 1) == 0:  # d is a power of two (dyadic)
        kk = (n.bit_length() - 1) - (d.bit_length() - 1)
        return [round_fraction(fmt, Fraction(kk), rm) for rm in RMS]
    return None


def specials(fmt):
    q = params(fmt)
    s = q["sign"]
    payloads = [1, 2, 3, (1 << (q["t"] - 1)) - 1, 1 << (q["t"] - 2)]
    out = [0, s, q["inf"], q["inf"] | s]
    for p in payloads:
        out.append(q["inf"] | q["qbit"] | p)
        out.append(q["inf"] | q["qbit"] | p | s)
        out.append(q["inf"] | p)
        out.append(q["inf"] | p | s)
    out.append(q["inf"] | q["qbit"])
    return out


def integers(fmt):
    q = params(fmt)
    p, emin, emax = q["p"], q["emin"], q["emax"]
    etie = emin - p
    vals = set()
    for n in range(-2, 3):
        vals.add(Fraction(n))
    for base in (p - 2, p - 1, p, p + 1, p + 2, p + 3,
                 -(p - 2), -(p - 1), -p, -(p + 1), -(p + 2), -(p + 3),
                 etie - 2, etie - 1, etie, etie + 1, etie + 2, etie + 3,
                 emin - 1, emin, emin + 1,
                 emax - 1, emax, emax + 1, emax + 2, emax + 3):
        vals.add(Fraction(base))
    out = set()
    for v in vals:
        x = encode_value(fmt, v)
        if x is not None:
            out.update(neighbours(fmt, x, 1))
    return sorted(out)


def cuts(fmt):
    q = params(fmt)
    p, emin, emax = q["p"], q["emin"], q["emax"]
    out = set()
    for tval in (emax + 1, emax + 2, emin - p, -(p + 1)):
        x = encode_value(fmt, Fraction(tval))
        if x is not None:
            out.update(neighbours(fmt, x, 3))
    return sorted(out)


def lattice(fmt):
    out = set()
    for s in (-10, -4, -1, 0, 1, 3, 6):
        sc = Fraction(2) ** s
        for m in range(-16, 17):
            x = encode_value(fmt, Fraction(m, 8) * sc)
            if x is not None:
                out.update(neighbours(fmt, x, 2))
    return sorted(out)


def tiny(fmt):
    q = params(fmt)
    s = q["sign"]
    out = set()
    for f in list(range(1, 10)) + [(1 << q["t"]) - i for i in range(1, 5)]:
        out.add(f)
        out.add(f | s)
    minnorm = 1 << q["t"]
    for d in range(-6, 7):
        out.add(minnorm + d)
        out.add((minnorm + d) | s)
    return sorted(out)


def strips(fmt, fn):
    q = params(fmt)
    p, emin, emax = q["p"], q["emin"], q["emax"]
    out = set()
    if fn == "exp2m1":
        # saturation strip: x from -(p+1) upward in fine steps
        for j in range(0, 49):
            x = encode_value(fmt, Fraction(-(p + 1)) + Fraction(j, 16))
            if x is not None:
                out.update(neighbours(fmt, x, 1))
        for j in range(1, 9):
            x = encode_value(fmt, Fraction(-(p + 1) - j, 1))
            if x is not None:
                out.update(neighbours(fmt, x, 2))
    else:
        # subnormal-result strip around the tie exponent
        etie = emin - p
        for j in range(-16, 65):
            x = encode_value(fmt, Fraction(etie) + Fraction(j, 8))
            if x is not None:
                out.update(neighbours(fmt, x, 1))
        # overflow strip below emax + 1
        for j in range(0, 33):
            x = encode_value(fmt, Fraction(emax + 1) - Fraction(j, 16))
            if x is not None:
                out.update(neighbours(fmt, x, 1))
    return sorted(out)


def log_powers(fmt, fn):
    """Exact-power encodings with +-1 ulp neighbours:
    log2 x=2^k (incl. subnormal x), log2p1 x=2^k-1."""
    q = params(fmt)
    p, emin, emax = q["p"], q["emin"], q["emax"]
    kmin = emin - p + 1
    ks = set(range(kmin, kmin + 6)) | set(range(emax - 5, emax + 1))
    ks |= set(range(-65, 66))
    ks |= set(range(kmin, emax + 1, 16))
    ks |= {-(p - 1), -p, p - 1, p}
    out = set()
    for k in sorted(ks):
        if k < kmin or k > emax:
            continue
        target = Fraction(2) ** k
        v = target if fn == "log2" else target - 1
        x = encode_value(fmt, v)
        if x is not None:
            out.update(neighbours(fmt, x, 1))
    return sorted(out)


def log_sqrt2(fmt, fn):
    """Significands straddling sqrt(2)*2^(p-1) (the exact
    recentring compare boundary) at several exponents."""
    import math as _math
    q = params(fmt)
    p, emin, emax = q["p"], q["emin"], q["emax"]
    s0 = _math.isqrt(2 * (1 << (2 * p - 2)))  # floor(sqrt2 2^(p-1))
    out = set()
    for eunb in (emin, -3, -1, 0, 1, 7, emax - 1):
        for s in range(s0 - 3, s0 + 5):
            if not (1 << (p - 1)) <= s < (1 << p):
                continue
            x = encode_value(fmt, Fraction(s) * Fraction(2) ** (eunb - (p - 1)))
            if x is not None:
                out.add(x)
            if fn == "log2p1":
                # w-side: 1+x with mm near sqrt2 (small spans)
                w = Fraction(s) * Fraction(2) ** (eunb - (p - 1))
                x2 = encode_value(fmt, w - 1)
                if x2 is not None:
                    out.add(x2)
    return sorted(out)


def log_near1(fmt):
    q = params(fmt)
    one = q["one"]
    out = set()
    for dlt in range(-6, 7):
        out.add(one + dlt)
    return sorted(out)


def log_tiny_ladder(fmt):
    """+-2^-j ladder across the log2p1 tiny threshold
    (2^-8/2^-9) with +-1 ulp neighbours."""
    q = params(fmt)
    p = q["p"]
    out = set()
    for j in range(1, p + 13):
        for vv in (Fraction(2) ** -j, -(Fraction(2) ** -j)):
            x = encode_value(fmt, vv)
            if x is not None:
                out.update(neighbours(fmt, x, 1))
    return sorted(out)


def log_pole(fmt):
    """log2p1 pole neighbourhood: x=-1 encodings +-6 and
    x = -1 + 2^-j approaches."""
    q = params(fmt)
    p = q["p"]
    out = set()
    neg_one = encode_value(fmt, Fraction(-1))
    if neg_one is not None:
        out.update(neighbours(fmt, neg_one, 6))
    for j in range(1, p + 1):
        x = encode_value(fmt, Fraction(-1) + Fraction(2) ** -j)
        if x is not None:
            out.update(neighbours(fmt, x, 1))
    return sorted(out)


def log_sticky(fmt):
    """log2p1 x = 2^k: w = 2^k+1 wide-span attractor (the
    s-division sticky line lives here)."""
    q = params(fmt)
    emax = q["emax"]
    out = set()
    for k in (8, 16, 32, 64, 128, 256, 512, 1000, emax - 1, emax - 2):
        if k < 1 or k > emax:
            continue
        x = encode_value(fmt, Fraction(2) ** k)
        if x is not None:
            out.update(neighbours(fmt, x, 2))
    return sorted(out)


def log_domain(fmt):
    out = set()
    for vv in (Fraction(-3, 2), Fraction(-2), Fraction(-100),
               Fraction(-1, 2), Fraction(-1, 8)):
        x = encode_value(fmt, vv)
        if x is not None:
            out.update(neighbours(fmt, x, 2))
    q = params(fmt)
    maxfin = ((q["emaxf"] - 1) << q["t"]) | q["fracmask"]
    out.add(maxfin | q["sign"])
    out.add(maxfin)
    return sorted(out)


# Spike-measured plain-class f64 maxima (input patterns only;
# scratch/sf2-explog/report.md Sec. 2.1).
HARDEST = {
    "f64": {
        "exp2": [0x3F5E4596526BF94D],
        "exp2m1": [0xBF73918E8608BD5B],
        "log2": [0x7FE61555F75885B4],
        "log2p1": [0x44EE499F19ECC9FB],
    },
    "f32": {"exp2": [], "exp2m1": [], "log2": [], "log2p1": []},
    "f16": {"exp2": [], "exp2m1": [], "log2": [], "log2p1": []},
}


def seeded(fmt, fn, n, seed):
    q = params(fmt)
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        x = rng.getrandbits(q["bits"])
        _, e, _, _ = fields(fmt, x)
        if e == q["emaxf"]:
            continue
        out.append(x)
    return out


def opname(fmt, fn):
    return f"msf{fmt[1:]}_{fn}"


def build_inputs_log(fmt, fn):
    fams = []
    fams.append(("specials", specials(fmt)))
    fams.append(("powers", log_powers(fmt, fn)))
    fams.append(("sqrt2", log_sqrt2(fmt, fn)))
    fams.append(("near1", log_near1(fmt)))
    fams.append(("tiny", sorted(set(tiny(fmt)) | set(log_tiny_ladder(fmt)))))
    fams.append(("lattice", lattice(fmt)))
    if fn == "log2p1":
        fams.append(("pole", log_pole(fmt)))
        fams.append(("sticky", log_sticky(fmt)))
    fams.append(("domain", log_domain(fmt)))
    hard = []
    for x in HARDEST[fmt][fn]:
        hard.extend(neighbours(fmt, x, 2))
    fams.append(("hardest", sorted(set(hard))))
    seed = 20261028 + (3333 if fn == "log2" else 4444) + int(fmt[1:])
    have = sum(len(v) for _, v in fams)
    fams.append(("seeded", seeded(fmt, fn, max(0, 1600 - have), seed)))
    seen = set()
    out = []
    for fam, xs in fams:
        for x in xs:
            if x not in seen:
                seen.add(x)
                out.append((fam, x))
    return out


def build_inputs(fmt, fn):
    if fn in ("log2", "log2p1"):
        return build_inputs_log(fmt, fn)
    fams = []
    fams.append(("specials", specials(fmt)))
    fams.append(("integers", integers(fmt)))
    fams.append(("cuts", cuts(fmt)))
    fams.append(("lattice", lattice(fmt)))
    fams.append(("tiny", tiny(fmt)))
    fams.append(("strips", strips(fmt, fn)))
    hard = []
    for x in HARDEST[fmt][fn]:
        hard.extend(neighbours(fmt, x, 2))
    fams.append(("hardest", sorted(set(hard))))
    seed = 20261028 + (0 if fn == "exp2" else 2222) + int(fmt[1:])
    have = sum(len(v) for _, v in fams)
    fams.append(("seeded", seeded(fmt, fn, max(0, 1600 - have), seed)))
    seen = set()
    out = []
    for fam, xs in fams:
        for x in xs:
            if x not in seen:
                seen.add(x)
                out.append((fam, x))
    return out


def main():
    outdir = sys.argv[1]
    exe = os.environ.get(
        "MSF_EXPLOG_DECIDER",
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "build", "explog", "explog_exhaustive.exe"))
    if not os.path.exists(exe):
        print(f"decider not found: {exe} (set MSF_EXPLOG_DECIDER)",
              file=sys.stderr)
        return 2
    jobs = []
    for fmt in FMTS:
        for fn in FNS:
            for fam, x in build_inputs(fmt, fn):
                jobs.append((fmt, fn, fam, x))
    inp = "".join(f"{opname(fmt, fn)} {x:x}\n"
                  for fmt, fn, _, x in jobs)
    proc = subprocess.run([exe, "decide"], input=inp,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout[-2000:])
        print("decider failed", file=sys.stderr)
        return 1
    decided = {}
    for line in proc.stdout.splitlines():
        t = line.split()
        if len(t) == 12:
            decided[(t[0], t[1])] = [
                (int(t[2 + 2 * i], 16), int(t[3 + 2 * i], 16))
                for i in range(5)
            ]
    if len(decided) != len(jobs):
        print(f"decider returned {len(decided)} of {len(jobs)}",
              file=sys.stderr)
        return 1
    files = {fmt: [] for fmt in FMTS}
    for fmt, fn, fam, x in jobs:
        op = opname(fmt, fn)
        exp = decided[(op, f"{x:x}")]
        mine = (expected_table_log(fmt, fn, x)
                if fn in ("log2", "log2p1")
                else expected_table(fmt, fn, x))
        if mine is not None and mine != exp:
            print(f"TABLE DISAGREE {op} {x:x}: settled {mine} "
                  f"decider {exp}", file=sys.stderr)
            return 1
        for rm, (rb, rf) in zip(RMS, exp):
            files[fmt].append(
                f"{op} {rm} {x:x} -> {rb:x} {rf:02x} mpfr-explog:{fam}")
    os.makedirs(outdir, exist_ok=True)
    total = 0
    for fmt in FMTS:
        path = os.path.join(outdir, f"explog-{fmt}.vec")
        with open(path, "w", newline="\n", encoding="utf-8") as fh:
            fh.write("# generated by tests/gen_vectors_explog.py"
                     " - do not edit (regenerate)\n")
            fh.write("# expectations: adaptive-precision MPFR bracket"
                     " decider (tests/explog_decider.c), five modes\n")
            fh.write("# ta lines independently decided (exact ties "
                     "exist at integer inputs; no relabel)\n")
            for line in files[fmt]:
                fh.write(line + "\n")
        total += len(files[fmt])
        print(f"wrote {path}: {len(files[fmt])} lines")
    print(f"total {total} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
