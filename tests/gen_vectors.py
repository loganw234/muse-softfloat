#!/usr/bin/env python3
"""Project-owned exact references + vector generation (SF-0 4.3).

Two independent references live here, test code only:

1. A bit-decode reference for classification and sign-bit operations:
   expected values are computed straight from the field definitions.
   Its strength is exhaustive input coverage, which catches generated
   tables/macros drifting from the standard's encodings.

2. An exact-rational reference for msf_pack_f64: the exact value is a
   Fraction, rounded per Clause 4/7 by a high-level algorithm that
   shares no code shape with the C kernel. Sticky-bearing cases are
   emitted ONLY when the (bits, flags) outcome is identical for every
   sticky fraction f in {1/4, 1/2, 3/4} (the C kernel is told only
   "nonzero"); non-invariant cases are counted and dropped, because
   they are not determined by the kernel's inputs.

Usage:
  gen_vectors.py directed OUTDIR          small committed sets
  gen_vectors.py f16-exhaustive OUTFILE   all 65536 encodings x 13 ops
  gen_vectors.py pack-sweep OUTFILE N     seeded random pack64 sweep
  gen_vectors.py board-smoke OUTFILE      small mixed set for the board
"""
import random
import sys
from fractions import Fraction
from pathlib import Path

FMTS = {  # name: (bits, precision, exp bits)
    "f16": (16, 11, 5),
    "f32": (32, 24, 8),
    "f64": (64, 53, 11),
}
FLAG_OVF, FLAG_UNF, FLAG_INX = 0x04, 0x08, 0x10
RMS = ["te", "tz", "tp", "tn", "ta"]


def fields(fmt, x):
    bits, p, w = FMTS[fmt]
    t = bits - 1 - w
    sign = (x >> (bits - 1)) & 1
    exp = (x >> t) & ((1 << w) - 1)
    frac = x & ((1 << t) - 1)
    return sign, exp, frac, ((1 << w) - 1), (1 << (t - 1))


def ref_class(fmt, x):
    sign, exp, frac, emaxf, qbit = fields(fmt, x)
    if exp == emaxf:
        if frac == 0:
            return 2 if sign else 9          # -inf / +inf
        return 1 if (frac & qbit) else 0    # quiet / signaling
    if exp == 0:
        if frac == 0:
            return 5 if sign else 6         # -zero / +zero
        return 4 if sign else 7             # subnormal
    return 3 if sign else 8                 # normal


def ref_preds(fmt, x):
    sign, exp, frac, emaxf, qbit = fields(fmt, x)
    isnan = exp == emaxf and frac != 0
    return {
        "is_sign_minus": sign,
        "is_normal": int(exp != 0 and exp != emaxf),
        "is_finite": int(exp != emaxf),
        "is_zero": int(exp == 0 and frac == 0),
        "is_subnormal": int(exp == 0 and frac != 0),
        "is_infinite": int(exp == emaxf and frac == 0),
        "is_nan": int(isnan),
        "is_signaling": int(isnan and not (frac & qbit)),
        "is_canonical": 1,
    }


def emit_encoding_lines(fmt, x, prov, out):
    sfx = fmt[1:]
    sign, exp, frac, emaxf, qbit = fields(fmt, x)
    signmask = 1 << (FMTS[fmt][0] - 1)
    out.append("msf%s_class - %x -> %x -- %s" % (sfx, x, ref_class(fmt, x), prov))
    for name, val in sorted(ref_preds(fmt, x).items()):
        out.append("msf%s_%s - %x -> %x -- %s" % (sfx, name, x, val, prov))
    out.append("msf%s_copy - %x -> %x -- %s" % (sfx, x, x, prov))
    out.append("msf%s_negate - %x -> %x -- %s" % (sfx, x, x ^ signmask, prov))
    out.append("msf%s_abs - %x -> %x -- %s" % (sfx, x, x & ~signmask, prov))
    out.append("msf%s_radix - %x -> 2 -- %s" % (sfx, x, prov))


def directed_encodings(fmt):
    bits, p, w = FMTS[fmt]
    t = bits - 1 - w
    emaxf = (1 << w) - 1
    qbit = 1 << (t - 1)
    fracs = [0, 1, 2, 3, qbit - 1, qbit, qbit + 1, qbit | 1,
             (1 << t) - 1, (1 << t) - 2, 0x155 & ((1 << t) - 1),
             0x2aa & ((1 << t) - 1)]
    exps = [0, 1, 2, emaxf // 2, emaxf - 2, emaxf - 1, emaxf]
    out = []
    for s in (0, 1):
        for e in exps:
            for f in fracs:
                out.append((s << (bits - 1)) | (e << t) | f)
    return out


# ---------------- pack64 rational reference ----------------

def round_int(x, rm, sign):
    fl = x.numerator // x.denominator
    rem = x - fl
    inexact = rem != 0
    half = Fraction(1, 2)
    inc = False
    if rm == "te":
        inc = rem > half or (rem == half and fl % 2 == 1)
    elif rm == "ta":
        inc = rem >= half
    elif rm == "tp":
        inc = (not sign) and inexact
    elif rm == "tn":
        inc = bool(sign) and inexact
    return fl + (1 if inc else 0), inexact


def pack_ref(sign, m, rm):
    """Exact binary64 pack of magnitude Fraction m, tininess AFTER."""
    if m == 0:
        return (sign << 63), 0
    emin, emax, p = -1022, 1023, 53
    e = m.numerator.bit_length() - m.denominator.bit_length()
    while Fraction(2) ** (e + 1) <= m:
        e += 1
    while Fraction(2) ** e > m:
        e -= 1
    scale = max(e, emin) - (p - 1)
    q, inexact = round_int(m / Fraction(2) ** scale, rm, sign)
    if q == 2 ** p:
        q >>= 1
        scale += 1
    v = q * Fraction(2) ** scale
    maxfinite = (2 - Fraction(1, 2 ** (p - 1))) * Fraction(2) ** emax
    if v > maxfinite:
        to_inf = rm in ("te", "ta") or (rm == "tp" and not sign) or (rm == "tn" and sign)
        enc = (0x7FF << 52) if to_inf else ((0x7FE << 52) | (2 ** 52 - 1))
        return (sign << 63) | enc, FLAG_OVF | FLAG_INX
    flags = 0
    if inexact:
        flags |= FLAG_INX
        if v < Fraction(2) ** emin:
            flags |= FLAG_UNF
    if q >= 2 ** (p - 1):
        return (sign << 63) | ((scale + (p - 1) + 1023) << 52) | (q - 2 ** (p - 1)), flags
    return (sign << 63) | q, flags


def pack_line(sign, sig, exp2, sticky, rm, prov):
    """Return the vector line, or None when not sticky-invariant."""
    if sig == 0:
        if sticky:
            return None  # outside kernel domain (callers jam into sig)
        results = {pack_ref(sign, Fraction(0), rm)}
    else:
        results = set()
        for fnum, fden in ((0, 1),) if not sticky else ((1, 4), (1, 2), (3, 4)):
            m = (sig + Fraction(fnum, fden)) * Fraction(2) ** exp2
            results.add(pack_ref(sign, m, rm))
    if len(results) != 1:
        return None
    (bits, flags), = results
    return ("internal.pack64 %s %d %d %032x %d -> %016x %02x %s"
            % (rm, sign, exp2, sig, 1 if sticky else 0, bits, flags, prov))


def pack_cases_from_scaled(sign, scale, q, tail, rm, prov, out, stats):
    """Exact value (q + tail) * 2^scale, tail a Fraction in [0,1)."""
    m = (q + tail) * Fraction(2) ** scale
    if m == 0:
        ln = pack_line(sign, 0, 0, False, rm, prov)
    else:
        # choose exp2 so sig fills the top of the 128-bit window
        e = m.numerator.bit_length() - m.denominator.bit_length()
        while Fraction(2) ** (e + 1) <= m:
            e += 1
        while Fraction(2) ** e > m:
            e -= 1
        exp2 = e - 127
        scaled = m / Fraction(2) ** exp2
        sig = scaled.numerator // scaled.denominator
        sticky = (scaled - sig) != 0
        ln = pack_line(sign, sig, exp2, sticky, rm, prov)
    if ln is None:
        stats[0] += 1
    else:
        out.append(ln)


def pack_directed(prov):
    out, stats = [], [0]
    tails = [Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4),
             Fraction(1, 2) - Fraction(1, 2 ** 40),
             Fraction(1, 2) + Fraction(1, 2 ** 40),
             Fraction(1, 2 ** 40), 1 - Fraction(1, 2 ** 40)]
    qs = [0, 1, 2, 3, 2 ** 51, 2 ** 52 - 2, 2 ** 52 - 1, 2 ** 52,
          2 ** 52 + 1, 2 ** 53 - 2, 2 ** 53 - 1]
    scales = [-1074, -1022 - 52, -52, -1, 0, 1023 - 52, 1023 - 51]
    for scale in scales:
        for q in qs:
            for tail in tails:
                for rm in RMS:
                    for sign in (0, 1):
                        pack_cases_from_scaled(sign, scale, q, tail, rm, prov, out, stats)
    # exponent extremes straight through the (sig, exp2) door
    for sig, exp2, sticky in [(1, -1074, False), (1, -1075, False),
                              (3, -1075, False), (1, -2000, False),
                              (2 ** 127, 896, False), (2 ** 127, 897, False),
                              (2 ** 128 - 1, 896, False), (2 ** 127, 2000, False),
                              (2 ** 127, -1149, True), (2 ** 128 - 1, -1150, False),
                              (0, 0, False)]:
        for rm in RMS:
            for sign in (0, 1):
                ln = pack_line(sign, sig, exp2, sticky, rm, prov)
                if ln is None:
                    stats[0] += 1
                else:
                    out.append(ln)
    return out, stats[0]


def pack_sweep(n, seed, prov):
    rng = random.Random(seed)
    out, dropped = [], 0
    tries = 0
    while len(out) < n and tries < n * 20:
        tries += 1
        sig = rng.getrandbits(rng.choice([1, 8, 53, 54, 64, 106, 128]))
        if sig == 0:
            continue
        # bias exponents toward the interesting ranges
        exp2 = rng.choice([rng.randint(-1200, -1000), rng.randint(-160, 60),
                           rng.randint(880, 1000), rng.randint(-1150, 950)])
        ln = pack_line(rng.randint(0, 1), sig, exp2, rng.random() < 0.5,
                       rng.choice(RMS), prov)
        if ln is None:
            dropped += 1
        else:
            out.append(ln)
    return out, dropped


def write(path, header, lines):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    print("wrote %s (%d lines)" % (path, len(lines)))


HDR = "# generated by tests/gen_vectors.py - do not edit (regenerate)\n"


def main(argv):
    mode = argv[1]
    if mode == "directed":
        outdir = Path(argv[2])
        for fmt in ("f16", "f32", "f64"):
            lines = []
            for x in directed_encodings(fmt):
                emit_encoding_lines(fmt, x, "exact-py:directed-encodings", lines)
            write(outdir / ("encodings-%s.vec" % fmt), HDR, lines)
        # copy_sign directed pairs over the f16 edge set + f32/f64 edges
        lines = []
        rng = random.Random(0x5EED)
        for fmt in ("f16", "f32", "f64"):
            enc = directed_encodings(fmt)
            bits = FMTS[fmt][0]
            signmask = 1 << (bits - 1)
            pairs = [(a, b) for a in enc[::17] for b in enc[::23]]
            if fmt == "f16":
                pairs += [(rng.getrandbits(16), rng.getrandbits(16))
                          for _ in range(4096)]
            for a, b in pairs:
                r = (a & ~signmask) | (b & signmask)
                lines.append("msf%s_copy_sign - %x %x -> %x -- exact-py:copysign-sample"
                             % (fmt[1:], a, b, r))
        write(outdir / "copysign.vec", HDR, lines)
        lines, dropped = pack_directed("exact-py:pack64-directed")
        write(outdir / "pack64.vec", HDR, lines)
        print("pack64 directed: dropped %d non-invariant cases" % dropped)
    elif mode == "f16-exhaustive":
        lines = []
        for x in range(65536):
            emit_encoding_lines("f16", x, "exact-py:f16-exhaustive", lines)
        write(argv[2], HDR, lines)
    elif mode == "pack-sweep":
        lines, dropped = pack_sweep(int(argv[3]), 0x5EED, "exact-py:pack64-sweep")
        write(argv[2], HDR, lines)
        print("pack sweep: dropped %d non-invariant cases" % dropped)
    elif mode == "board-smoke":
        lines = []
        for fmt in ("f16", "f32", "f64"):
            for x in directed_encodings(fmt)[::9]:
                emit_encoding_lines(fmt, x, "exact-py:directed-encodings", lines)
        lines += pack_directed("exact-py:pack64-directed")[0][::37]
        write(argv[2], HDR, lines)
    else:
        raise SystemExit("unknown mode %s" % mode)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
