# audit.py - independent exact audit of interval_host output vs
# the catalogue inputs. Recomputes every exact quantity from the
# stored bit patterns with Fractions (does not trust the TSV
# exact column; cross-checks it). Exit nonzero on any violation.
# Usage: audit.py CATALOGUE.tsv HOST-OUT.txt [--expect-fail-note]
import struct
import sys
from fractions import Fraction


def f64(bits_hex):
    b = int(bits_hex, 16)
    return Fraction(struct.unpack(">d", struct.pack(">Q", b))[0])


def f32(bits_hex):
    b = int(bits_hex, 16)
    return Fraction(struct.unpack(">f", struct.pack(">I", b))[0])


def is_nan64(bits_hex):
    b = int(bits_hex, 16)
    return ((b >> 52) & 0x7FF) == 0x7FF and (b & ((1 << 52) - 1)) != 0


def is_nan32(bits_hex):
    b = int(bits_hex, 16)
    return ((b >> 23) & 0xFF) == 0xFF and (b & ((1 << 23) - 1)) != 0


def is_inf64(bits_hex):
    b = int(bits_hex, 16)
    return ((b >> 52) & 0x7FF) == 0x7FF and (b & ((1 << 52) - 1)) == 0


def lo_contains(lo_hex, ex, conv, exp_bits, frac_bits):
    # True iff endpoint value <= ex, with infinities honoured.
    b = int(lo_hex, 16)
    if ((b >> frac_bits) & ((1 << exp_bits) - 1)) == (1 << exp_bits) - 1 \
            and (b & ((1 << frac_bits) - 1)) == 0:
        return b >> (exp_bits + frac_bits) == 1  # -inf <= ex, +inf not
    return conv(lo_hex) <= ex


def hi_contains(hi_hex, ex, conv, exp_bits, frac_bits):
    b = int(hi_hex, 16)
    if ((b >> frac_bits) & ((1 << exp_bits) - 1)) == (1 << exp_bits) - 1 \
            and (b & ((1 << frac_bits) - 1)) == 0:
        return b >> (exp_bits + frac_bits) == 0  # +inf >= ex, -inf not
    return conv(hi_hex) >= ex


def disc_exact(O, D, C, r):
    L = [O[i] - C[i] for i in range(3)]
    a = sum(D[i] * D[i] for i in range(3))
    b = sum(L[i] * D[i] for i in range(3))
    c = sum(L[i] * L[i] for i in range(3)) - r * r
    return b * b - a * c


RT, RTUBE = Fraction(2), Fraction(1, 2)


def torus_F(O, D, t):
    x, y, z = (O[i] + t * D[i] for i in range(3))
    s = x * x + y * y + z * z + RT * RT - RTUBE * RTUBE
    return s * s - 4 * RT * RT * (x * x + y * y)


def torus_first_root(O, D):
    prev, pf = Fraction(0), torus_F(O, D, Fraction(0))
    assert pf > 0
    for i in range(1, 11 * 512 + 1):
        t = Fraction(i, 512)
        v = torus_F(O, D, t)
        if v < 0:
            a, b = prev, t
            while b - a > Fraction(2) ** -30:
                m = (a + b) / 2
                if torus_F(O, D, m) < 0:
                    b = m
                else:
                    a = m
            return a, b
        prev, pf = t, v
    return None


def box_exact(O, D, lo, hi):
    tmin, tmax = Fraction(0), None
    for i in range(3):
        if D[i] == 0:
            if O[i] < lo[i] or O[i] > hi[i]:
                return "MISS", None
            continue
        t1 = (lo[i] - O[i]) / D[i]
        t2 = (hi[i] - O[i]) / D[i]
        a, b = (t1, t2) if t1 <= t2 else (t2, t1)
        tmin = max(tmin, a)
        tmax = b if tmax is None else min(tmax, b)
    if tmax is not None and tmin > tmax:
        return "MISS", None
    return "HIT", (tmin, tmax)


def parse_host(path):
    rays = {}
    for ln in open(path):
        if not ln.startswith("RAY "):
            continue
        kv = dict(tok.split("=", 1) for tok in ln.split()[1:])
        rays[int(kv["id"])] = kv
    return rays


def main():
    cat_path, host_path = sys.argv[1], sys.argv[2]
    host = parse_host(host_path)
    violations = []
    decided_wrong = []
    flips = []
    counts = {}          # (family, stage) -> [hit, miss, unc]
    naive_disagree = {}  # family -> n

    def bump(fam, stage, cls):
        c = counts.setdefault((fam, stage), [0, 0, 0])
        c[{"HIT": 0, "MISS": 1, "UNCERTAIN": 2}[cls]] += 1

    nrows = 0
    for ln in open(cat_path):
        if ln.startswith("#") or not ln.strip():
            continue
        f = ln.rstrip("\n").split("\t")
        rid, fam, kind = int(f[0]), f[1], f[2]
        O = [f64(x) for x in f[4:7]]
        D = [f64(x) for x in f[7:10]]
        g = [f64(x) for x in f[10:16]]
        exact_col, naive_col = f[16], f[17]
        nrows += 1
        h = host.get(rid)
        if h is None:
            violations.append("row %d missing from host output" % rid)
            continue

        if kind == "sphere":
            ex = disc_exact(O, D, g[0:3], g[3])
            exact = "HIT" if ex >= 0 else "MISS"
            # containment of stage-1/2 endpoint bits (NaN endpoint
            # can only arise from overflow; then the stage must be
            # UNCERTAIN and containment is judged vacuous-by-refusal)
            if is_nan32(h["s1lo"]) or is_nan32(h["s1hi"]):
                if h["s1"] != "UNCERTAIN":
                    violations.append("row %d s1 NaN endpoint decided" % rid)
            elif not (lo_contains(h["s1lo"], ex, f32, 8, 23)
                      and hi_contains(h["s1hi"], ex, f32, 8, 23)):
                violations.append("row %d s1 containment" % rid)
            if is_nan64(h["s2lo"]) or is_nan64(h["s2hi"]):
                if h["s2"] != "UNCERTAIN":
                    violations.append("row %d s2 NaN endpoint decided" % rid)
            elif not (lo_contains(h["s2lo"], ex, f64, 11, 52)
                      and hi_contains(h["s2hi"], ex, f64, 11, 52)):
                violations.append("row %d s2 containment" % rid)
            for st in ("s1", "s2", "s3", "final"):
                bump(fam, st, h[st])
                if h[st] != "UNCERTAIN" and h[st] != exact:
                    decided_wrong.append("row %d %s=%s exact=%s" %
                                         (rid, st, h[st], exact))
            dec = [h[s] for s in ("s1", "s2", "s3") if h[s] != "UNCERTAIN"]
            if len(set(dec)) > 1:
                flips.append("row %d decided flip %s" % (rid, dec))
            if fam == "guard" and h["s3"] != "UNCERTAIN":
                violations.append("row %d guard s3=%s not UNCERTAIN" %
                                  (rid, h["s3"]))
        elif kind == "box":
            exact, trange = box_exact(O, D, g[0:3], g[3:6])
            bump(fam, "box", h["dec"])
            if h["dec"] != "UNCERTAIN" and h["dec"] != exact:
                decided_wrong.append("row %d box=%s exact=%s" %
                                     (rid, h["dec"], exact))
            if exact == "HIT" and trange is not None and trange[1] is not None:
                if not is_nan64(h["tmin"]) and not is_nan64(h["tmax"]):
                    if not (f64(h["tmin"]) <= trange[0] and
                            (is_inf64(h["tmax"]) or f64(h["tmax"]) >= trange[1])):
                        violations.append("row %d box outer containment" % rid)
        elif kind == "torus":
            root = torus_first_root(O, D)
            exact = "HIT" if root else "MISS"
            bump(fam, "torus", h["dec"])
            if h["dec"] != "UNCERTAIN" and h["dec"] != exact:
                decided_wrong.append("row %d torus=%s exact=%s" %
                                     (rid, h["dec"], exact))
            if h["dec"] == "HIT" and root:
                brlo, brhi = f64(h["brlo"]), f64(h["brhi"])
                if not (torus_F(O, D, brhi) < 0):
                    violations.append("row %d torus F(brhi) not <0" % rid)
                if not (brlo <= root[1] and root[0] <= brhi):
                    violations.append("row %d torus bracket misses root" % rid)
                if brlo > root[1]:
                    violations.append("row %d torus bracket after root" % rid)
        else:
            violations.append("row %d unknown kind" % rid)
            continue

        if exact_col != exact:
            violations.append("row %d TSV exact col %s != recomputed %s" %
                              (rid, exact_col, exact))
        if naive_col != exact:
            naive_disagree[fam] = naive_disagree.get(fam, 0) + 1

    # stage monotonicity: UNCERTAIN non-increasing s1->s2->s3 overall
    def unc(stage):
        return sum(v[2] for (fm, st), v in counts.items() if st == stage)

    mono_ok = unc("s1") >= unc("s2") >= unc("s3")
    if not mono_ok:
        violations.append("stage UNCERTAIN not non-increasing: %d %d %d" %
                          (unc("s1"), unc("s2"), unc("s3")))

    print("rows=%d" % nrows)
    for (fam, st) in sorted(counts):
        v = counts[(fam, st)]
        print("counts fam=%s stage=%s HIT=%d MISS=%d UNCERTAIN=%d" %
              (fam, st, v[0], v[1], v[2]))
    print("naive_vs_exact_disagreements=%s" %
          dict(sorted(naive_disagree.items())))
    print("containment_violations=%d decided_wrong=%d flips=%d" %
          (len(violations), len(decided_wrong), len(flips)))
    for msg in (violations + decided_wrong + flips)[:20]:
        print("FAIL:", msg)
    ok = not violations and not decided_wrong and not flips
    print("AUDIT", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
