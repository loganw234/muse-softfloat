#!/usr/bin/env python3
"""fastdec.py - fast integer-only twin of mydecide.decide.

Same contract, dyadic-int hot path (no Fractions except at the final
encode step). Validated by asserting equality with mydecide.decide on
samples before use (selftest mode).
"""
import sys
from fractions import Fraction
from math import isqrt

sys.path.insert(0, "scratch/verifier-w5alg2")
from mydecide import FMTS, specials, decode, encode_value  # noqa: E402
from mydecide import OVERFLOW, UNDERFLOW, INEXACT  # noqa: E402


def _choose(rm, n, exact, above_mid, on_mid):
    if exact or rm in ("tz", "tn"):
        return n
    if rm == "tp" or above_mid:
        return n + 1
    if on_mid:
        return n + 1 if rm == "ta" else (n if n % 2 == 0 else n + 1)
    return n


def _ge_pow2(M, E, k):
    """M * 2^E >= 2^k ? (M > 0 int, E int, k int)."""
    if E >= 0:
        return (M << E) >= (1 << k)
    return M >= (1 << (k - E))


def round_sqrt_fast(fi, M, E):
    """Round sqrt(M * 2^E), M > 0 int, E int. [(bits,flags)]x5."""
    f = FMTS[fi]
    p = f["p"]
    log2S = M.bit_length() - 1 + E
    e = log2S // 2
    while _ge_pow2(M, E, 2 * (e + 1)):
        e += 1
    while not _ge_pow2(M, E, 2 * e):
        e -= 1
    def decide_at(Mm, kk):
        # Decide floor/midpoint of the dyadic value Mm * 2^kk, Mm > 0.
        if kk >= 0:
            R = Mm << kk
            n = isqrt(R)
            exact = n * n == R
            d4 = 4 * R - (2 * n + 1) ** 2
            return n, exact, d4 > 0, d4 == 0
        t = -kk
        n = isqrt(Mm >> t)
        exact = n * n * (1 << t) == Mm
        num = 4 * Mm - (2 * n + 1) ** 2 * (1 << t)
        return n, exact, num > 0, num == 0

    out = []
    for rm in RMS_ORDER:
        # unbounded precision-p granularity (the overflow judge)
        ku = E - 2 * (e - (p - 1))
        n_u, exact_u, above_u, on_u = decide_at(M, ku)
        w = (n_u if exact_u else _choose(rm, n_u, False, above_u, on_u))
        thr_max = f["emax"] + 1 - (e - (p - 1))
        if thr_max <= 0 or w >= (1 << thr_max):
            bits = f["inf"] if rm in ("te", "ta", "tp") else f["maxfin"]
            out.append((bits, OVERFLOW | INEXACT))
            continue
        thr_min = f["emin"] - (e - (p - 1))
        tiny = thr_min > 0 and w < (1 << thr_min)
        if e >= f["emin"]:
            n_d, exact_d, above_d, on_d = n_u, exact_u, above_u, on_u
            ulp_d_shift = e - (p - 1)
        else:
            ulp_d_shift = f["emin"] - (p - 1)
            kd = E - 2 * ulp_d_shift
            n_d, exact_d, above_d, on_d = decide_at(M, kd)
        c = n_d if exact_d else _choose(rm, n_d, False, above_d, on_d)
        val = Fraction(c) * Fraction(2) ** ulp_d_shift
        inexact = not exact_d
        flags = 0
        if inexact:
            flags |= INEXACT
            if tiny:
                flags |= UNDERFLOW
        out.append((encode_value(fi, val), flags))
    return out


RMS_ORDER = ("te", "tz", "tp", "tn", "ta")


def decide_fast(fi, a, b):
    s = specials(fi, a, b)
    if s is not None:
        return s
    _, _, sa, ea = decode(fi, a)
    _, _, sb, eb = decode(fi, b)
    A2, B2 = sa * sa, sb * sb
    e2a, e2b = 2 * ea, 2 * eb
    if e2a >= e2b:
        M = (A2 << (e2a - e2b)) + B2
        E = e2b
    else:
        M = A2 + (B2 << (e2b - e2a))
        E = e2a
    assert M > 0
    return round_sqrt_fast(fi, M, E)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        from mydecide import decide as slow
        n = mm = 0
        for line in sys.stdin:
            tk = line.split()
            if len(tk) != 3:
                continue
            fi, a, b = int(tk[0]), int(tk[1], 16), int(tk[2], 16)
            n += 1
            if decide_fast(fi, a, b) != slow(fi, a, b):
                mm += 1
                if mm <= 5:
                    print(f"MISM fi={fi} a={a:x} b={b:x}")
                    print(f"  fast={decide_fast(fi, a, b)}")
                    print(f"  slow={slow(fi, a, b)}")
        print(f"selftest: pairs={n} mismatches={mm}")
        return 0 if mm == 0 else 1
    for line in sys.stdin:
        tk = line.split()
        if len(tk) != 3:
            continue
        fi, a, b = int(tk[0]), int(tk[1], 16), int(tk[2], 16)
        print(" ".join(f"{rb:x} {rf:02x}" for rb, rf in decide_fast(fi, a, b)))


if __name__ == "__main__":
    sys.exit(main())
