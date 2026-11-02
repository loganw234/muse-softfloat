"""Independent Ek re-derivation for the scalar truncating evaluation.

Own implementation from the design-entry recurrence (ledger/parcel-w4trig.md
Section 2 as amended): one truncating op (or truncated constant) errs by at
most 2^(1-W) relative; Horner from the smallest term with rho_k
amplification; Taylor tails by first-neglected-term/(1-ratio); delta branch
from the shifted cosine series. Bounds use ZMAX=(pi_hi/4)^2 with a rational
pi ceiling, S_MIN=0.9003 lower bound for sin(u)/u on [0,pi/4], D_MIN for
D(z). Result: per-stage bit counts B with Ek <= 2^-B; code must use an
exponent <= B-9 (9-bit margin). Compares against the committed header
{200,242,370} and the generator's {146,242,370}.
"""
import math
import sys
from fractions import Fraction

PI_HI = Fraction(314159265358979323846264338327950288419716939937511,
                 10**50)
ZMAX = (PI_HI / 4) ** 2
S_MIN = Fraction(9003, 10000)
D_MIN = Fraction(9496, 10000)
STAGES = (160, 256, 384)
NTERMS = (21, 29, 39)  # per generator/stage printout
HEADER_EK = (200, 242, 370)
GENERATOR_EK = (146, 242, 370)


def tail(kind, nterms):
    if kind == "sin":
        t = ZMAX**nterms / Fraction(math.factorial(2 * nterms + 1))
        r = ZMAX / Fraction((2 * nterms + 2) * (2 * nterms + 3))
    else:
        t = 2 * ZMAX**nterms / Fraction(math.factorial(2 * nterms + 2))
        r = ZMAX / Fraction((2 * nterms + 3) * (2 * nterms + 4))
    return t / (1 - r)


def stage_bound(w, nterms):
    eps = Fraction(2, 2**w)
    e_u = 2 * eps + eps * eps
    e_z = 2 * e_u + e_u * e_u + eps

    def horner(kind, val_min):
        e = eps
        for k in range(nterms - 2, -1, -1):
            if kind == "sin":
                rho = ZMAX / Fraction((2 * k + 2) * (2 * k + 3))
            else:
                rho = ZMAX / Fraction((2 * k + 3) * (2 * k + 4))
            e_prod = e_z + e + e_z * e + eps
            e = (eps + rho * e_prod) / (1 - rho) + eps
        return e + tail(kind, nterms) / val_min

    e_s = horner("sin", S_MIN)
    e_sin = e_u + e_s + e_u * e_s + eps
    e_d = horner("delta", D_MIN)
    e_del = e_z + e_d + e_z * e_d + eps
    return max(e_sin, e_del)


def bits_of(bound):
    b = 0
    while Fraction(2) ** -(b + 1) >= bound:
        b += 1
    return b


def main():
    print("W  N   bound_bits  code_margin_ok(need exp<=bound-9)")
    fail = 0
    for w, n, hc, gc in zip(STAGES, NTERMS, HEADER_EK, GENERATOR_EK):
        bound = stage_bound(w, n)
        b = bits_of(bound)
        need = b - 9
        h_ok = hc <= need
        g_ok = gc <= need
        print(f"{w} {n:3d} {b:6d}   header_exp={hc} "
              f"{'OK' if h_ok else 'TOO-NARROW'}  generator_exp={gc} "
              f"{'OK' if g_ok else 'TOO-NARROW'}")
        if not h_ok:
            fail += 1
    print("header_too_narrow_stages:", fail)
    return 0


sys.exit(main())
