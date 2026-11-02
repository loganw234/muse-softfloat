#!/usr/bin/env python3
# 03_audit.py - INDEPENDENT exact-rational containment audit.
# Written from the geometry (|O+tD-C|^2=r^2, slab intersection,
# torus implicit F) without consulting the parcel audit or trusting
# the TSV decisions. Checks the copy's host RAY output against
# exact Fraction arithmetic over the stored bit patterns.
import struct
import sys
from fractions import Fraction

VROOT = "C:/Users/logan/source/repos/Muse-Softfloat"
COPY = VROOT + "/worktrees/verify4-interval"
OUT = VROOT + "/scratch/verifier-w4interval"
TSV = COPY + "/tests/interval_catalogue.tsv"
HOST = sys.argv[1] if len(sys.argv) > 1 else OUT + "/build/host_out.txt"
TAG = sys.argv[2] if len(sys.argv) > 2 else "baseline"

import numpy as np


def f64_of_bits(b):
    return struct.unpack(">d", struct.pack(">Q", b))[0]


def f32_of_bits(b):
    return struct.unpack(">f", struct.pack(">I", b))[0]


def F(x):
    # exact Fraction of a finite python float; None for nan/inf
    import math
    if math.isnan(x) or math.isinf(x):
        return None
    return Fraction(x)


def H(bits, w=64):
    return int(bits, 16)


# ---------- load TSV ----------
rows = []  # (id, fam, kind, prov, O, D, g, exact_col, naive_col, extra)
with open(TSV) as fh:
    for ln in fh:
        if ln.startswith("#") or not ln.strip():
            continue
        p = ln.rstrip("\n").split("\t")
        assert len(p) == 19, len(p)
        i = int(p[0])
        O = [H(x) for x in p[4:7]]
        D = [H(x) for x in p[7:10]]
        g = [H(x) for x in p[10:16]]
        rows.append(dict(id=i, fam=p[1], kind=p[2], prov=p[3],
                          O=O, D=D, g=g, exact=p[16], naive=p[17],
                          extra=p[18]))
assert len(rows) == 710, len(rows)

# ---------- load host RAY output ----------
host = {}
summary = None
sha = None
with open(HOST) as fh:
    for ln in fh:
        if ln.startswith("RAY "):
            d = {}
            for tok in ln.split()[1:]:
                k, v = tok.split("=", 1)
                d[k] = v
            host[int(d["id"])] = d
        elif ln.startswith("SUMMARY "):
            summary = ln.strip()
        elif ln.startswith("HOST_SHA256 "):
            sha = ln.split()[1]
assert len(host) == 710, len(host)

# ---------- exact geometry (independent derivations) ----------
def exact_sphere(O, D, C, r):
    # |O + t D - C|^2 = r^2 ; a t^2 + 2 b t + c = 0 with
    # L = O - C, a = D.D, b = L.D, c = L.L - r^2.
    # HIT (touch or cross) iff half-discriminant b^2 - a c >= 0.
    L = [O[i] - C[i] for i in range(3)]
    a = sum(D[i] * D[i] for i in range(3))
    b = sum(L[i] * D[i] for i in range(3))
    c = sum(L[i] * L[i] for i in range(3)) - r * r
    return b * b - a * c


def naive_sphere_f32(O, D, C, r):
    f = np.float32
    Of = [f(v) for v in O]
    Dv = [f(v) for v in D]
    Cf = [f(v) for v in C]
    L = [Of[i] - Cf[i] for i in range(3)]
    a = Dv[0] * Dv[0] + Dv[1] * Dv[1] + Dv[2] * Dv[2]
    b = L[0] * Dv[0] + L[1] * Dv[1] + L[2] * Dv[2]
    c = L[0] * L[0] + L[1] * L[1] + L[2] * L[2] - f(r) * f(r)
    v = b * b - a * c
    return "TANGENT0" if v == 0 else ("HIT" if v > 0 else "MISS")


def naive_sphere_f64(O, D, C, r):
    L = [O[i] - C[i] for i in range(3)]
    a = D[0] * D[0] + D[1] * D[1] + D[2] * D[2]
    b = L[0] * D[0] + L[1] * D[1] + L[2] * D[2]
    c = L[0] * L[0] + L[1] * L[1] + L[2] * L[2] - r * r
    v = b * b - a * c
    return "TANGENT0" if v == 0 else ("HIT" if v > 0 else "MISS")


RT, RTU = Fraction(2), Fraction(1, 2)


def torus_F(O, D, t):
    x = [O[i] + t * D[i] for i in range(3)]
    s = x[0] * x[0] + x[1] * x[1] + x[2] * x[2] + RT * RT - RTU * RTU
    return s * s - 4 * RT * RT * (x[0] * x[0] + x[1] * x[1])


def torus_exact_class(O, D):
    # HIT iff some dyadic sample is < 0 (then continuity from F(0)>0
    # proves a root); MISS proven separately by subdivision.
    assert torus_F(O, D, Fraction(0)) > 0
    n = 11 * 256
    for i in range(1, n + 1):
        if torus_F(O, D, Fraction(i, 256)) < 0:
            return "HIT"
    return "MISS"


def torus_prove_positive(O, D, alo, ahi):
    # exact rational interval proof that F > 0 on [alo, ahi];
    # returns True iff proven (subdivision, depth cap 60).
    lin = [[O[i], D[i]] for i in range(3)]

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

    sq = [pmul(lin[i], lin[i]) for i in range(3)]
    s = padd(padd(padd(sq[0], sq[1]), sq[2]), [RT * RT - RTU * RTU])
    Ft = padd(pmul(s, s), [-4 * RT * RT * c for c in padd(sq[0], sq[1])])

    def iv(a, b):
        lo = hi = Fraction(0)
        pa, pb = Fraction(1), Fraction(1)
        for c in Ft:
            x, y = (pa, pb) if pa <= pb else (pb, pa)
            if c >= 0:
                lo += c * x
                hi += c * y
            else:
                lo += c * y
                hi += c * x
            pa, pb = pa * a, pb * b
            if pa > pb:
                pa, pb = pb, pa
        return lo, hi

    stack = [(alo, ahi, 0)]
    while stack:
        a, b, dep = stack.pop()
        lo, _ = iv(a, b)
        if lo > 0:
            continue
        if dep >= 60:
            return False
        m = (a + b) / 2
        stack.append((a, m, dep + 1))
        stack.append((m, b, dep + 1))
    return True


def box_exact(O, D, lo, hi):
    tmin, tmax = Fraction(0), None
    for i in range(3):
        if D[i] == 0:
            if O[i] < lo[i] or O[i] > hi[i]:
                return "MISS"
            continue
        t1 = (lo[i] - O[i]) / D[i]
        t2 = (hi[i] - O[i]) / D[i]
        a, b = (t1, t2) if t1 <= t2 else (t2, t1)
        if a > tmin:
            tmin = a
        if tmax is None or b < tmax:
            tmax = b
    if tmax is not None and tmin > tmax:
        return "MISS"
    return "HIT"


def naive_box(O, D, lo, hi):
    import math
    tmin, tmax = -math.inf, math.inf
    with np.errstate(all="ignore"):
        for i in range(3):
            t1 = float(np.float64(lo[i] - O[i]) / np.float64(D[i]))
            t2 = float(np.float64(hi[i] - O[i]) / np.float64(D[i]))
            a, b = (t1, t2) if t1 <= t2 else (t2, t1)
            tmin = a if a > tmin else tmin
            tmax = b if b < tmax else tmax
    return "HIT" if tmax >= max(tmin, 0.0) else "MISS"


def naive_torus(O, D):
    for i in range(111):
        t = i * 0.1
        x = [O[j] + t * D[j] for j in range(3)]
        s = x[0] * x[0] + x[1] * x[1] + x[2] * x[2] + 4.0 - 0.25
        if s * s - 16.0 * (x[0] * x[0] + x[1] * x[1]) < 0:
            return "HIT"
    return "MISS"


viol, dw1, dw2, dw3, dwf, nanrows = [], [], [], [], [], []
flips = []
tsv_exact_bad, tsv_naive_bad = [], []
guard_not_unc = []
box_bad, torus_bad = [], []
fam_stats = {}
s1u = s2u = s3u = 0
naive_dis_tan = 0

for r in rows:
    O = [F(f64_of_bits(b)) for b in r["O"]]
    D = [F(f64_of_bits(b)) for b in r["D"]]
    h = host[r["id"]]
    fs = fam_stats.setdefault(r["fam"], dict(n=0, viol=0, dw=0))
    fs["n"] += 1
    if r["kind"] == "sphere":
        C = [F(f64_of_bits(b)) for b in r["g"][:3]]
        rv = F(f64_of_bits(r["g"][3]))
        ex = exact_sphere(O, D, C, rv)
        ex_cls = "HIT" if ex >= 0 else "MISS"
        if ex_cls != r["exact"]:
            tsv_exact_bad.append(r["id"])
        Of = [f64_of_bits(b) for b in r["O"]]
        Df = [f64_of_bits(b) for b in r["D"]]
        Cf = [f64_of_bits(r["g"][i]) for i in range(3)]
        rf = f64_of_bits(r["g"][3])
        is32 = r["fam"] in ("tangent400", "limb", "ordinary")
        nv = naive_sphere_f32(Of, Df, Cf, rf) if is32 else naive_sphere_f64(Of, Df, Cf, rf)
        if nv != r["naive"]:
            tsv_naive_bad.append((r["id"], r["naive"], nv))
        if r["fam"] == "tangent400" and r["exact"] != r["naive"]:
            naive_dis_tan += 1
        # host decisions
        s1, s2, s3, fin = h["s1"], h["s2"], h["s3"], h["final"]
        lo1 = F(f32_of_bits(int(h["s1lo"], 16)))
        hi1 = F(f32_of_bits(int(h["s1hi"], 16)))
        lo2 = F(f64_of_bits(int(h["s2lo"], 16)))
        hi2 = F(f64_of_bits(int(h["s2hi"], 16)))
        for tag, bv in (("s1", (int(h["s1lo"], 16), int(h["s1hi"], 16), 32)),
                        ("s2", (int(h["s2lo"], 16), int(h["s2hi"], 16), 64))):
            lob, hib, w = bv
            defe = f32_of_bits if w == 32 else f64_of_bits
            import math as _m
            loe, hie = defe(lob), defe(hib)
            if _m.isnan(loe) or _m.isnan(hie):
                # unprovable endpoint: safe only with UNCERTAIN (else
                # already counted as decided-wrong below)
                nanrows.append((r["id"], r["fam"], tag))
                fs["viol"] += 1
            else:
                bad = False
                if loe == float("inf") or hie == float("-inf"):
                    bad = True  # empty interval cannot contain finite exact
                else:
                    if not _m.isinf(loe) and ex < F(loe):
                        bad = True
                    if not _m.isinf(hie) and ex > F(hie):
                        bad = True
                if bad:
                    viol.append((r["id"], r["fam"], tag))
                    fs["viol"] += 1
        dec = []
        for tag, s in (("s1", s1), ("s2", s2), ("s3", s3), ("final", fin)):
            if s == "UNCERTAIN":
                if tag == "s1":
                    s1u += 1
                elif tag == "s2":
                    s2u += 1
                elif tag == "s3":
                    s3u += 1
            else:
                dec.append(s)
                want = ex_cls
                if s != want:
                    {"s1": dw1, "s2": dw2, "s3": dw3,
                     "final": dwf}[tag].append((r["id"], r["fam"], s, want))
                    fs["dw"] += 1
        if len(set(dec)) > 1:
            flips.append((r["id"], r["fam"], s1, s2, s3, fin))
        if r["fam"] == "guard" and s3 != "UNCERTAIN":
            guard_not_unc.append((r["id"], s3))
    elif r["kind"] == "box":
        lo = [F(f64_of_bits(b)) for b in r["g"][:3]]
        hi = [F(f64_of_bits(b)) for b in r["g"][3:]]
        Of = [f64_of_bits(b) for b in r["O"]]
        Df = [f64_of_bits(b) for b in r["D"]]
        lof = [f64_of_bits(b) for b in r["g"][:3]]
        hif = [f64_of_bits(b) for b in r["g"][3:]]
        ex = box_exact(O, D, lo, hi)
        if ex != r["exact"]:
            tsv_exact_bad.append(r["id"])
        if naive_box(Of, Df, lof, hif) != r["naive"]:
            tsv_naive_bad.append((r["id"], r["naive"], "naive-mismatch"))
        if h["dec"] != "UNCERTAIN" and h["dec"] != ex:
            box_bad.append((r["id"], h["dec"], ex))
            fs["dw"] += 1
    else:  # torus
        Of = [f64_of_bits(b) for b in r["O"]]
        Df = [f64_of_bits(b) for b in r["D"]]
        ex = torus_exact_class(O, D)
        if ex != r["exact"]:
            tsv_exact_bad.append(r["id"])
        if naive_torus(Of, Df) != r["naive"]:
            tsv_naive_bad.append((r["id"], r["naive"], "naive-mismatch"))
        cls = h["dec"]
        brlo = f64_of_bits(int(h["brlo"], 16))
        brhi = f64_of_bits(int(h["brhi"], 16))
        if cls == "HIT":
            ok = (torus_F(O, D, Fraction(0)) > 0 and
                  F(brhi) is not None and torus_F(O, D, F(brhi)) < 0)
            if not ok:
                torus_bad.append((r["id"], "HIT-bracket-invalid"))
                fs["dw"] += 1
        elif cls == "MISS":
            if not torus_prove_positive(O, D, Fraction(0), Fraction(11)):
                torus_bad.append((r["id"], "MISS-unproven"))
                fs["dw"] += 1
        if cls != "UNCERTAIN" and cls != ex:
            torus_bad.append((r["id"], cls, ex))
            fs["dw"] += 1

print("=== audit", TAG, "===")
print("rows:", len(rows), "host:", len(host))
print("sha:", sha)
print("summary:", summary)
print("s1u/s2u/s3u:", s1u, s2u, s3u)
print("HARD-VIOLATIONS:", len(viol), viol[:20])
print("NAN-INTERVAL-ROWS:", len(nanrows), nanrows[:20])
print("DECIDED-WRONG s1:", len(dw1), dw1[:20])
print("DECIDED-WRONG s2:", len(dw2), dw2[:20])
print("DECIDED-WRONG s3:", len(dw3), dw3[:20])
print("DECIDED-WRONG final:", len(dwf), dwf[:20])
print("FLIPS:", len(flips), flips[:20])
print("TSV-EXACT-MISMATCH:", len(tsv_exact_bad), tsv_exact_bad[:20])
print("TSV-NAIVE-MISMATCH:", len(tsv_naive_bad), tsv_naive_bad[:20])
print("GUARD-NOT-UNCERTAIN:", len(guard_not_unc), guard_not_unc)
print("BOX-BAD:", len(box_bad), box_bad)
print("TORUS-BAD:", len(torus_bad), torus_bad)
print("TANGENT400 naive-vs-exact disagreements:",
      sum(1 for r in rows if r["fam"] == "tangent400" and r["exact"] != r["naive"]))
for fam, st in sorted(fam_stats.items()):
    print("fam", fam, st)
