"""verifier-p0 independent round-and-pack reference (Fractions only).

No logic shared with tests/gen_vectors.py (never read). Contract taken from
src/msf_internal.h + src/msf_formats.h constants + IEEE 754-2019 rules.
"""
from fractions import Fraction
import random
import subprocess

P = 53
EMIN = -1022
EMAX = 1023
BIAS = 1023
EXP_MAX = 0x7FF
FRAC_BITS = 52
SIGN_MASK = 0x8000000000000000
INFINITY = 0x7FF0000000000000
FRAC_MASK = 0x000FFFFFFFFFFFFF
MAXFINITE = (EXP_MAX - 1 << FRAC_BITS) | FRAC_MASK  # 0x7FEFFFFFFFFFFFFF

F_INV, F_DZ, F_OVF, F_UNF, F_INEX = 0x01, 0x02, 0x04, 0x08, 0x10
# rm: 0 te 1 tz 2 tp 3 tn 4 ta


def rint_mag(mag, rm, sign):
    """Round nonnegative Fraction mag to int per rm (sign for directed)."""
    fl = mag.numerator // mag.denominator
    rem = mag - fl
    if rem == 0:
        return fl, False
    if rm == 0:  # ties to even
        if rem < Fraction(1, 2):
            return fl, True
        if rem > Fraction(1, 2):
            return fl + 1, True
        return (fl if fl % 2 == 0 else fl + 1), True
    if rm == 4:  # ties away (from zero == up for magnitude)
        if rem < Fraction(1, 2):
            return fl, True
        return fl + 1, True
    if rm == 1:  # toward zero
        return fl, True
    # directed: tp rounds toward +inf, tn toward -inf
    up = (rm == 2 and sign == 0) or (rm == 3 and sign == 1)
    return (fl + 1 if up else fl), True


def ref_pack(sign, exp2, sig, f, rm):
    """Exact reference. f is Fraction in [0,1): the sticky fraction."""
    v = (sig + f) * (Fraction(2) ** exp2)
    if v == 0:
        return (SIGN_MASK if sign else 0), 0
    e2 = v.numerator.bit_length() - v.denominator.bit_length()
    if v < Fraction(2) ** e2:
        e2 -= 1
    assert Fraction(2) ** e2 <= v < Fraction(2) ** (e2 + 1), (sign, exp2, sig, f)
    if e2 >= EMIN:
        cand_ex = v / Fraction(2) ** (e2 - (P - 1))
    else:
        cand_ex = v / Fraction(2) ** (EMIN - (P - 1))
    rnd, inex = rint_mag(cand_ex, rm, sign)
    if e2 >= EMIN and rnd == 2 ** P:
        rnd = 2 ** (P - 1)
        e2 += 1
    if e2 < EMIN and rnd == 2 ** (P - 1):
        e2 = EMIN  # rounded up to smallest normal
    flags = 0
    if inex:
        flags |= F_INEX
    if e2 > EMAX:
        flags |= F_OVF | F_INEX
        to_inf = rm in (0, 4) or (rm == 2 and sign == 0) or (rm == 3 and sign == 1)
        return ((SIGN_MASK if sign else 0) | (INFINITY if to_inf else MAXFINITE)), flags
    if e2 >= EMIN:
        assert rnd >= 2 ** (P - 1), ("tiny-normal?", sign, exp2, sig, f, rm, hex(rnd))
        return ((SIGN_MASK if sign else 0) | ((e2 + BIAS) << FRAC_BITS)
                | (rnd - 2 ** (P - 1))), flags
    # subnormal / zero
    if inex and rnd < 2 ** (P - 1):
        flags |= F_UNF
    if rnd >= 2 ** (P - 1):
        return ((SIGN_MASK if sign else 0) | ((EMIN + BIAS) << FRAC_BITS)
                | (rnd - 2 ** (P - 1))), flags
    return ((SIGN_MASK if sign else 0) | rnd), flags


def gen_cases():
    C = []  # (sign, exp2, sig, sticky, rms)
    ALL = [0, 1, 2, 3, 4]
    SN = (1 << 52) * (2 ** -1074)  # smallest normal as value; build via sig/exp2
    # smallest-normal boundary both sides, all modes, both signs
    C.append((0, -1074, 1 << 52, 0, ALL))      # exact smallest normal
    C.append((1, -1074, 1 << 52, 0, ALL))
    C.append((0, -1074, (1 << 52) - 1, 0, ALL))  # largest subnormal exact
    C.append((0, -1075, (1 << 53) - 1, 0, ALL))  # half-ulp below smallest normal (tie)
    C.append((1, -1075, (1 << 53) - 1, 0, ALL))
    C.append((0, -1074, 1 << 52, 1, ALL))      # just above smallest normal
    C.append((0, -1074, (1 << 52) + 1, 0, ALL))  # one ulp above
    C.append((0, -1074, 1, 0, ALL))            # smallest subnormal exact
    C.append((0, -1074, 5, 0, ALL))            # exact subnormal
    # ties: te vs ta at exact halves
    C.append((0, -1, (1 << 53) + 1, 0, ALL))   # 2^52 + 0.5
    C.append((1, -1, (1 << 53) + 1, 0, ALL))
    C.append((0, -1, (1 << 53) + 3, 0, ALL))   # 2^52 + 1.5
    C.append((1, -1, (1 << 53) + 3, 0, ALL))
    C.append((0, -1, (1 << 53) + 1, 1, ALL))   # tie + sticky -> strictly above
    C.append((0, -1, (1 << 53) - 1, 0, ALL))   # 2^52 - 0.5 (tie, even is up)
    # overflow deliveries
    C.append((0, 970, (1 << 54) - 1, 0, ALL))  # 2^1024 - 2^970
    C.append((1, 970, (1 << 54) - 1, 0, ALL))
    C.append((0, 1024, 1, 0, ALL))             # exact 2^1024
    C.append((1, 1024, 1, 0, ALL))
    C.append((0, 971, (1 << 53) - 1, 0, ALL))  # exact maxfinite
    C.append((0, 971, (1 << 53) - 1, 1, ALL))  # just above maxfinite
    C.append((1, 971, (1 << 53) - 1, 1, ALL))
    C.append((0, 971, 1 << 53, 0, ALL))        # 2^1024 - 2^971... (e_bits 1024)
    # round-to-zero / directed basics
    C.append((0, -2, 5, 0, ALL))               # 1.25 exact
    C.append((0, -53, 3, 0, ALL))              # tiny normal-range? 3*2^-53 exact
    C.append((1, -2, 7, 0, ALL))               # -1.75 exact
    C.append((0, -1, 3, 0, ALL))               # 1.5 exact
    # huge / tiny exponents
    C.append((0, 2000, 1, 0, ALL))
    C.append((0, 2000, (1 << 128) - 1, 0, ALL))
    C.append((0, -2000, 1, 0, ALL))            # deep underflow to zero
    C.append((1, -2000, 1, 1, ALL))
    C.append((0, -2000, (1 << 128) - 1, 1, ALL))
    C.append((0, -1074, 1, 1, ALL))            # smallest subnormal + sticky
    C.append((0, 0, 0, 0, ALL))                # zero
    C.append((1, 0, 0, 0, ALL))
    C.append((0, -60, 1 << 100, 0, ALL))       # wide sig exact normal
    C.append((0, -60, (1 << 100) + 1, 1, ALL))  # wide sig + sticky
    C.append((0, 100, 1 << 100, 0, ALL))
    # zero-sig with sticky (outside domain; record C behavior separately)
    return C


def main():
    rng = random.Random(0xC10C)
    rows = []
    for (s, e, g, st, rms) in gen_cases():
        for rm in rms:
            rows.append((s, e, g, st, rm))
    # seeded random sweep
    for _ in range(3000):
        g = rng.getrandbits(128)
        if rng.random() < 0.3:
            g &= (1 << rng.choice([53, 54, 55, 64, 100])) - 1 or 1
        e = rng.choice([rng.randint(-1100, -1000), rng.randint(-60, 60),
                        rng.randint(900, 1100), rng.randint(-3000, 3000)])
        s = rng.getrandbits(1)
        st = rng.getrandbits(1)
        rows.append((s, e, g, st, rng.randrange(5)))
    # evaluate reference (sticky=1 sampled at two fractions)
    cases, skipped = [], 0
    for (s, e, g, st, rm) in rows:
        if g == 0:
            cases.append((s, e, g, st, rm, ref_pack(s, e, g, Fraction(0), rm), "exact0"))
            continue
        if st == 0:
            cases.append((s, e, g, st, rm, ref_pack(s, e, g, Fraction(0), rm), "exact"))
        else:
            r1 = ref_pack(s, e, g, Fraction(1, 2), rm)
            r2 = ref_pack(s, e, g, 1 - Fraction(1, 2 ** 70), rm)
            r3 = ref_pack(s, e, g, Fraction(1, 2 ** 70), rm)
            if r1 == r2 == r3:
                cases.append((s, e, g, st, rm, r1, "sticky-invariant"))
            else:
                skipped += 1
    print("cases:", len(cases), "f-sensitive skipped:", skipped)
    # feed probe
    inp = "".join("pack %d %d %032x %d %d\n" % (s, e, g, st, rm)
                  for (s, e, g, st, rm, _, _) in cases)
    p = subprocess.run(
        [r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-p0\vpack_probe.exe"],
        input=inp, capture_output=True, text=True, timeout=120)
    assert p.returncode == 0, p.stderr[:500]
    lines = p.stdout.splitlines()
    assert len(lines) == len(cases), (len(lines), len(cases))
    bad = 0
    for (case, ln) in zip(cases, lines):
        (s, e, g, st, rm, (eb, ef), tag) = case
        bits, fl = ln.split()
        if bits != "%016x" % eb or fl != "%02x" % ef:
            bad += 1
            if bad <= 20:
                print("MISMATCH pack %d %d %032x %d %d [%s]: C=%s %s ref=%016x %02x"
                      % (s, e, g, st, rm, tag, bits, fl, eb, ef))
    print("mismatches:", bad, "of", len(cases))


main()
