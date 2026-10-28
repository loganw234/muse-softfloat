# gen_interval_catalogue.py - frozen ray catalogue for the Step 1c
# interval workload (board/interval_workload.c), generated fresh
# for this parcel. The deciding oracle is exact rational
# arithmetic (Fraction) on the exact values of the stored binary64
# bit patterns. Host floating arithmetic appears ONLY in the
# indicted "naive" column (the comparison exhibit), never as an
# oracle. Deterministic: seeded, no timestamps; regeneration must
# be byte-identical (brief gate).
#
# Usage: gen_interval_catalogue.py [out.tsv]
# Default out: interval_catalogue.tsv next to this file.
#
# Columns (tab separated, '#' lines are comments):
#   id family kind provenance
#   ox oy oz dx dy dz          binary64 bit patterns, 16 hex digits
#   g0 g1 g2 g3 g4 g5          sphere: cx cy cz r 0 0
#                              box:    lox loy loz hix hiy hiz
#                              torus:  all zero (R=2, r=1/2 frozen
#                                      in the workload)
#   exact naive exact_extra
# Sphere class is the discriminant-sign class: disc >= 0 -> HIT
# (tangent touches), disc < 0 -> MISS. exact_extra for sphere is
# the exact discriminant as num/den; for box the exact t range
# "tmin,tmax" as num/den (or empty/parallel-out); for torus an
# exact first-root bracket "lo,hi" as num/den (or none).
import math
import random
import struct
import sys
from fractions import Fraction

import numpy as np

SEED_TANGENT = 4242


def bits64_of_float(x):
    return struct.unpack(">Q", struct.pack(">d", float(x)))[0]


def frac_of_bits64(b):
    return Fraction(struct.unpack(">d", struct.pack(">Q", b))[0])


def hex64(x):
    # x: Python float (exact binary64 value intended)
    return "%016x" % bits64_of_float(x)


def f32_float(x):
    # exact widening of the binary32 nearest x, as a Python float
    return float(np.float32(x))


def frac(x):
    return Fraction(float(x))


def fracs(v):
    return [frac(x) for x in v]


# ---- exact sphere oracle -------------------------------------------
def disc_exact(O, D, C, r):
    L = [O[i] - C[i] for i in range(3)]
    a = sum(D[i] * D[i] for i in range(3))
    b = sum(L[i] * D[i] for i in range(3))
    c = sum(L[i] * L[i] for i in range(3)) - r * r
    return b * b - a * c


def class_of_sign(fr):
    return "HIT" if fr >= 0 else "MISS"


def disc_naive_f32(O, D, C, r):
    f = np.float32
    L = [f(float(O[i])) - f(float(C[i])) for i in range(3)]
    Dv = [f(float(v)) for v in D]
    a = Dv[0] * Dv[0] + Dv[1] * Dv[1] + Dv[2] * Dv[2]
    b = L[0] * Dv[0] + L[1] * Dv[1] + L[2] * Dv[2]
    c = L[0] * L[0] + L[1] * L[1] + L[2] * L[2] - f(float(r)) * f(float(r))
    v = b * b - a * c
    return "TANGENT0" if v == 0 else ("HIT" if v > 0 else "MISS")


def disc_naive_f64(O, D, C, r):
    L = [float(O[i]) - float(C[i]) for i in range(3)]
    Dv = [float(v) for v in D]
    a = Dv[0] * Dv[0] + Dv[1] * Dv[1] + Dv[2] * Dv[2]
    b = L[0] * Dv[0] + L[1] * Dv[1] + L[2] * Dv[2]
    c = L[0] * L[0] + L[1] * L[1] + L[2] * L[2] - float(r) * float(r)
    v = b * b - a * c
    return "TANGENT0" if v == 0 else ("HIT" if v > 0 else "MISS")


ROWS = []


def add_sphere(family, prov, O, D, C, r, naive32):
    ex = disc_exact(fracs(O), fracs(D), fracs(C), frac(r))
    nv = disc_naive_f32(O, D, C, r) if naive32 else disc_naive_f64(O, D, C, r)
    g = [hex64(v) for v in list(C) + [r, 0.0, 0.0]]
    ROWS.append([family, "sphere", prov,
                 [hex64(v) for v in O], [hex64(v) for v in D], g,
                 class_of_sign(ex), nv, "%d/%d" % (ex.numerator, ex.denominator)])
    return ex


# ---- families -------------------------------------------------------
def fam_tangent400():
    # Tangent-by-construction: D=(1,0,0), cy^2+cz^2 within a few
    # binary32 ulps of r^2=1, centre 2^k ahead. Re-derived from the
    # survey construction; fresh stream, 400 kept rows.
    rng = random.Random(SEED_TANGENT)
    kept = 0
    trial = 0
    while kept < 400:
        trial += 1
        k = rng.choice([4, 8, 12, 16])
        cx = f32_float((2.0 ** k) * rng.uniform(1.0, 1.9))
        th = rng.uniform(0, 6.283)
        eps = rng.choice([-3, -2, -1, 1, 2, 3])
        rad = 1.0 + eps * 2.0 ** -24
        cy = f32_float(math.cos(th) * rad)
        cz = f32_float(math.sin(th) * rad)
        O = [0.0, 0.0, 0.0]
        D = [1.0, 0.0, 0.0]
        C = [cx, cy, cz]
        if disc_exact(fracs(O), fracs(D), fracs(C), frac(1.0)) == 0:
            continue
        add_sphere("tangent400", "tangent-by-construction seed=%d trial=%d "
                   "k=%d eps_ulps=%d" % (SEED_TANGENT, trial, k, eps),
                   O, D, C, 1.0, naive32=True)
        kept += 1


def fam_adv2k():
    # Adversarial distance-2^k family, binary64-native: exact disc
    # is a few binary64 ulps of 1 while b^2 ~ 2^2k cancels.
    for k in (10, 20, 30, 40):
        for m in (1, 4):
            cx = 2.0 ** k
            cy = 1.0 - m * 2.0 ** -53
            assert frac(cy) == 1 - m * Fraction(2) ** -53
            add_sphere("adv2k", "distance-2^k inside k=%d m=%d" % (k, m),
                       [0.0] * 3, [1.0, 0.0, 0.0], [cx, cy, 0.0], 1.0,
                       naive32=False)
            cy = 1.0 + m * 2.0 ** -52
            assert frac(cy) == 1 + m * Fraction(2) ** -52
            add_sphere("adv2k", "distance-2^k outside k=%d m=%d" % (k, m),
                       [0.0] * 3, [1.0, 0.0, 0.0], [cx, cy, 0.0], 1.0,
                       naive32=False)
    add_sphere("adv2k", "exact tangent k=20 cy=1",
               [0.0] * 3, [1.0, 0.0, 0.0], [2.0 ** 20, 1.0, 0.0], 1.0,
               naive32=False)
    for k in (20, 30):
        cx = (2.0 ** k) * (1.0 + 2.0 ** -20)
        assert frac(cx) == Fraction(2) ** k * (1 + Fraction(2) ** -20)
        add_sphere("adv2k", "distance-2^k(1+2^-20) inside k=%d" % k,
                   [0.0] * 3, [1.0, 0.0, 0.0], [cx, 1.0 - 2.0 ** -53, 0.0],
                   1.0, naive32=False)
        add_sphere("adv2k", "distance-2^k(1+2^-20) outside k=%d" % k,
                   [0.0] * 3, [1.0, 0.0, 0.0], [cx, 1.0 + 2.0 ** -52, 0.0],
                   1.0, naive32=False)


def f32_from_bits(b):
    return float(np.float32(struct.unpack(">f", struct.pack(">I", b))[0]))


def fam_limb():
    # Limb scanline: direction y stepped by single binary32 ulps
    # across the silhouette of a far sphere (exact disc decreases
    # monotonically in py here, so integer binary search on the
    # binary32 bit pattern finds the exact crossing).
    O = [0.0, 0.0, 0.0]
    C = [8192.0, 0.0, 0.0]
    r = 1024.0

    def disc_py(py):
        return disc_exact(fracs(O), fracs([1.0, py, 0.0]), fracs(C), frac(r))

    lo = struct.unpack(">I", struct.pack(">f", 0.0))[0]   # disc > 0
    hi = struct.unpack(">I", struct.pack(">f", 1.0))[0]   # disc < 0
    assert disc_py(f32_from_bits(lo)) > 0 > disc_py(f32_from_bits(hi))
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if disc_py(f32_from_bits(mid)) > 0:
            lo = mid
        else:
            hi = mid
    start = lo - 29
    for step in range(260):
        py = f32_from_bits(start + step)
        add_sphere("limb", "limb scanline step=%d py_bits32=%08x "
                   "(exact crossing between steps 29 and 30)"
                   % (step, start + step),
                   O, [1.0, py, 0.0], C, r, naive32=True)


def fam_guard():
    # Stage-3 proof-guard cases: exact disc decidable rationally,
    # but binary64 products overflow (2^600 scale) or underflow
    # (2^-600 scale) the expansion. Stage 3 must yield UNCERTAIN.
    for s, tag in ((2.0 ** 600, "overflow-2^600"), (2.0 ** -600, "underflow-2^-600")):
        cy_in = s * (1.0 - 2.0 ** -52)
        cy_out = s * (1.0 + 2.0 ** -51)
        assert frac(cy_in) == frac(s) * (1 - Fraction(2) ** -52)
        assert frac(cy_out) == frac(s) * (1 + Fraction(2) ** -51)
        add_sphere("guard", "%s inside (exact HIT)" % tag,
                   [0.0] * 3, [1.0, 0.0, 0.0], [s, cy_in, 0.0], s,
                   naive32=False)
        add_sphere("guard", "%s outside (exact MISS)" % tag,
                   [0.0] * 3, [1.0, 0.0, 0.0], [s, cy_out, 0.0], s,
                   naive32=False)


def fam_ordinary():
    cases = [
        ("central hit", [0.0] * 3, [1.0, 0.0, 0.0], [5.0, 0.0, 0.0], 1.0),
        ("clear miss", [0.0] * 3, [1.0, 0.0, 0.0], [5.0, 3.0, 0.0], 1.0),
        ("diagonal hit", [0.0] * 3, [1.0, 1.0, 1.0], [4.0, 4.0, 4.0], 2.0),
        ("diagonal miss", [0.0] * 3, [1.0, 1.0, 0.0], [4.0, 4.0, 3.0], 1.0),
        ("origin inside", [5.0, 0.0, 0.0], [0.0, 1.0, 0.0], [5.0, 0.0, 0.0], 2.0),
        ("far offset hit", [4096.0, 4096.0, 8192.0], [0.0, 0.0, -1.0],
         [4096.0, 4096.0, -8192.0], 3000.0),
        ("far offset miss", [4096.0, 4096.0, 8192.0], [1.5, 0.0, -1.0],
         [4096.0, 4096.0, -8192.0], 3000.0),
        ("small scale miss", [0.0] * 3, [1.0, 0.0, 0.0],
         [2.0 ** -30, 2.0 ** -29, 0.0], 2.0 ** -30),
    ]
    for name, O, D, C, r in cases:
        Oh = [f32_float(v) for v in O]
        Dh = [f32_float(v) for v in D]
        Ch = [f32_float(v) for v in C]
        add_sphere("ordinary", name, Oh, Dh, Ch, f32_float(r), naive32=True)


# ---- exact box oracle ----------------------------------------------
def box_exact(O, D, lo, hi):
    tmin, tmax = Fraction(0), None  # None = +inf
    for i in range(3):
        if D[i] == 0:
            if O[i] < lo[i] or O[i] > hi[i]:
                return "MISS", "parallel-out"
            continue
        t1 = (lo[i] - O[i]) / D[i]
        t2 = (hi[i] - O[i]) / D[i]
        a, b = (t1, t2) if t1 <= t2 else (t2, t1)
        if a > tmin:
            tmin = a
        if tmax is None or b < tmax:
            tmax = b
    if tmax is not None and tmin > tmax:
        return "MISS", "empty"
    return "HIT", "%d/%d,%s" % (tmin.numerator, tmin.denominator,
                                 "inf" if tmax is None else
                                 "%d/%d" % (tmax.numerator, tmax.denominator))


def box_naive(O, D, lo, hi):
    # Indicted exhibit: host binary64 slabs with propagating
    # min/max and NO axis-parallel branch (survey E4 policies).
    def pmin(a, b):
        return float("nan") if (math.isnan(a) or math.isnan(b)) else min(a, b)

    def pmax(a, b):
        return float("nan") if (math.isnan(a) or math.isnan(b)) else max(a, b)

    tmin, tmax = -math.inf, math.inf
    with np.errstate(all="ignore"):
        for i in range(3):
            t1 = float(np.float64(lo[i] - O[i]) / np.float64(D[i]))
            t2 = float(np.float64(hi[i] - O[i]) / np.float64(D[i]))
            tmin = pmax(tmin, pmin(t1, t2))
            tmax = pmin(tmax, pmax(t1, t2))
    return "HIT" if tmax >= max(tmin, 0.0) else "MISS"


def fam_box():
    lo = [0.0, 0.0, 0.0]
    hi = [1.0, 1.0, 1.0]
    cases = [
        ("face plane x=0, ray in face (survey E4)", [0.0, -1.0, 0.5], [0.0, 1.0, 0.0]),
        ("edge line x=0,z=0", [0.0, -1.0, 0.0], [0.0, 1.0, 0.0]),
        ("parallel outside x=2", [2.0, -1.0, 0.5], [0.0, 1.0, 0.0]),
        ("parallel 1ulp outside x=1+2^-52", [1.0 + 2.0 ** -52, -1.0, 0.5], [0.0, 1.0, 0.0]),
        ("axis through centre", [-1.0, 0.5, 0.5], [1.0, 0.0, 0.0]),
        ("negative direction", [2.0, 0.5, 0.5], [-1.0, 0.0, 0.0]),
        ("pointing away", [2.0, 0.5, 0.5], [1.0, 0.0, 0.0]),
        ("origin inside", [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]),
        ("corner entry diagonal", [-1.0, -1.0, 0.5], [1.0, 1.0, 0.0]),
        ("diagonal miss above", [-1.0, 0.5, 2.0], [1.0, 0.0, 0.0]),
        ("face plane z=1 from below-face", [0.5, -2.0, 1.0], [0.0, 1.0, 0.0]),
        ("slab order miss", [-3.0, -0.5, 0.5], [1.0, 1.0, 0.0]),
    ]
    for name, O, D in cases:
        ex, extra = box_exact(fracs(O), fracs(D), fracs(lo), fracs(hi))
        nv = box_naive(O, D, lo, hi)
        ROWS.append(["box", "box", name,
                     [hex64(v) for v in O], [hex64(v) for v in D],
                     [hex64(v) for v in lo + hi], ex, nv, extra])


# ---- exact torus oracle ---------------------------------------------
RT, RTUBE = Fraction(2), Fraction(1, 2)


def torus_F(O, D, t):
    x, y, z = (O[i] + t * D[i] for i in range(3))
    s = x * x + y * y + z * z + RT * RT - RTUBE * RTUBE
    return s * s - 4 * RT * RT * (x * x + y * y)


def torus_exact_bracket(O, D, tmax=Fraction(11)):
    # Exact scan at dyadic points: a point with F<0 plus F(0)>0
    # proves a first root in between (polynomial continuity);
    # bisect the exact sign change to width <= 2^-24.
    assert torus_F(O, D, Fraction(0)) > 0
    prev = Fraction(0)
    n = int(tmax * 256)
    for i in range(1, n + 1):
        t = Fraction(i, 256)
        if torus_F(O, D, t) < 0:
            a, b = prev, t
            while b - a > Fraction(2) ** -24:
                m = (a + b) / 2
                if torus_F(O, D, m) < 0:
                    b = m
                else:
                    a = m
            return "HIT", "%d/%d,%d/%d" % (a.numerator, a.denominator,
                                            b.numerator, b.denominator)
        prev = t
    return "MISS", "none"


def torus_prove_miss(O, D, tmax=Fraction(11)):
    # Exact rational interval subdivision of the quartic in t
    # (monomial form, exact Fraction interval evaluation).
    def pmul(a, b):
        r = [Fraction(0)] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                r[i + j] += x * y
        return r

    def padd(a, b):
        n = max(len(a), len(b))
        return [(a[i] if i < len(a) else Fraction(0)) +
                (b[i] if i < len(b) else Fraction(0)) for i in range(n)]

    lin = [[O[i], D[i]] for i in range(3)]
    sq = [pmul(lin[i], lin[i]) for i in range(3)]
    s = padd(padd(padd(sq[0], sq[1]), sq[2]), [RT * RT - RTUBE * RTUBE])
    Ft = padd(pmul(s, s), [-4 * RT * RT * c for c in padd(sq[0], sq[1])])

    def iv_eval(a, b):
        lo = hi = Fraction(0)
        pa, pb = Fraction(1), Fraction(1)
        for c in Ft:
            plo, phi = (pa, pb) if pa <= pb else (pb, pa)
            if c >= 0:
                lo += c * plo
                hi += c * phi
            else:
                lo += c * phi
                hi += c * plo
            pa, pb = pa * a, pb * b
            if pa > pb:
                pa, pb = pb, pa
        return lo, hi

    stack = [(Fraction(0), tmax, 0)]
    while stack:
        a, b, depth = stack.pop()
        lo, _ = iv_eval(a, b)
        if lo > 0:
            continue
        assert depth < 40, "torus miss proof did not close"
        m = (a + b) / 2
        stack.append((a, m, depth + 1))
        stack.append((m, b, depth + 1))


def torus_naive_march(O, D):
    # Indicted exhibit: host binary64 point samples at h=0.1.
    def F(t):
        x, y, z = (float(O[i]) + t * float(D[i]) for i in range(3))
        s = x * x + y * y + z * z + 4.0 - 0.25
        return s * s - 16.0 * (x * x + y * y)

    for i in range(0, 111):
        if F(i * 0.1) < 0:
            return "HIT"
    return "MISS"


def fam_torus():
    cases = [
        ("clean miss z=3", [0.0, -5.0, 3.0], [0.0, 1.0, 0.0]),
        ("central hit z=0", [0.0, -5.0, 0.0], [0.0, 1.0, 0.0]),
        ("ordinary hit z=1/4", [0.0, -5.0, 0.25], [0.0, 1.0, 0.0]),
        ("grazing chord R=2 r=1/2 z=0.499", [0.0, -5.0, 0.499], [0.0, 1.0, 0.0]),
        ("grazing chord phase-shifted y0=-5.037",
         [0.0, -5.037, 0.499], [0.0, 1.0, 0.0]),
    ]
    for name, O, D in cases:
        ex, extra = torus_exact_bracket(fracs(O), fracs(D))
        if ex == "MISS":
            torus_prove_miss(fracs(O), fracs(D))
        nv = torus_naive_march(O, D)
        ROWS.append(["torus", "torus", name,
                     [hex64(v) for v in O], [hex64(v) for v in D],
                     [hex64(0.0)] * 6, ex, nv, extra])


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else None
    if out_path is None:
        import os
        out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "interval_catalogue.tsv")
    fam_tangent400()
    fam_adv2k()
    fam_limb()
    fam_guard()
    fam_ordinary()
    fam_box()
    fam_torus()
    lines = [
        "# interval_catalogue.tsv - frozen Step 1c ray catalogue.",
        "# Generated by tests/gen_interval_catalogue.py (exact Fraction",
        "# oracle; naive column is the indicted host-arithmetic exhibit).",
        "# Regeneration must be byte-identical. Columns: id family kind",
        "# provenance ox oy oz dx dy dz g0..g5 exact naive exact_extra.",
        "# All geometry words are binary64 bit patterns (16 hex). Sphere",
        "# class = discriminant sign (disc>=0 HIT). Torus R=2 r=1/2.",
    ]
    counts = {}
    for i, row in enumerate(ROWS, 1):
        fam, kind, prov, O, D, g, ex, nv, extra = row
        counts[fam] = counts.get(fam, 0) + 1
        lines.append("\t".join([str(i), fam, kind, prov] + O + D + g +
                                [ex, nv, extra]))
    with open(out_path, "w", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote %s rows=%d by_family=%s" %
          (out_path, len(ROWS), dict(sorted(counts.items()))))


if __name__ == "__main__":
    main()
