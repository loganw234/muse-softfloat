"""check_expansions.py CATALOGUE DUMPOUT STREAMNEW
Exact-oracle check of the stage-3 expansion sums for every
sphere row: distilled A/B/C list sums must equal exact
a=D.D, b=L.D, c=L.L-r^2 (L=O-C) and the assembled D list sum
must equal exact disc=b^2-a*c, all as Fractions from the raw
binary64 patterns. Equality is required on every row the new
stage 3 decides; UNCERTAIN rows are reported, not required.
Also cross-checks the computed disc sign vs the catalogue
exact column and exact_extra Fraction where present.
"""
import sys
from fractions import Fraction


def bits_to_frac(b):
    sign = -1 if (b >> 63) else 1
    exp = (b >> 52) & 0x7FF
    frac = b & ((1 << 52) - 1)
    if exp == 0x7FF:
        return None  # non-finite term: sums become None (inexact)
    if exp == 0:
        return Fraction(sign * frac) * Fraction(2) ** (-1074)
    return Fraction(sign * ((1 << 52) + frac)) * Fraction(2) ** (exp - 1075)


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


cat = {}
fams = {}
for line in open(sys.argv[1], encoding="ascii"):
    if line.startswith("#") or not line.strip():
        continue
    f = line.rstrip("\n").split("\t")
    if f[2] != "sphere":
        continue
    rid = int(f[0])
    O = [bits_to_frac(int(f[4 + i], 16)) for i in range(3)]
    D = [bits_to_frac(int(f[7 + i], 16)) for i in range(3)]
    C = [bits_to_frac(int(f[10 + i], 16)) for i in range(3)]
    r = bits_to_frac(int(f[13], 16))
    L = [o - c for o, c in zip(O, C)]
    a = dot(D, D)
    b = dot(L, D)
    c = dot(L, L) - r * r
    disc = b * b - a * c
    cat[rid] = (a, b, c, disc, f[16], f[18])
    fams[rid] = f[1]

s3cls = {}
for line in open(sys.argv[3], encoding="ascii"):
    if line.startswith("RAY ") and "s3=" in line:
        kv = dict(t.partition("=")[::2] for t in line.split()[1:])
        s3cls[int(kv["id"])] = kv["s3"]

cur = None
exp = {}
checked = decided = extra_cross = 0
fails = []
unc_rows = []
for line in open(sys.argv[2], encoding="ascii"):
    t = line.split()
    if not t:
        continue
    if t[0] == "ROW":
        cur = int(t[1])
        exp = {}
    elif t[0] == "EXP":
        exp[t[1]] = [bits_to_frac(int(x, 16)) for x in t[3:]]
        assert len(exp[t[1]]) == int(t[2])
    elif t[0] == "CLS":
        a, b, c, disc, exact, extra = cat[cur]
        sign_cls = "MISS" if disc < 0 else "HIT"
        if sign_cls != exact:
            fails.append((cur, "disc-sign vs catalogue", sign_cls, exact))
        try:
            if Fraction(extra) == disc:
                extra_cross += 1
            else:
                fails.append((cur, "disc vs exact_extra", str(disc), extra))
        except (ValueError, ZeroDivisionError):
            pass
        sums = {k: (None if any(x is None for x in v) else sum(v, Fraction(0)))
                for k, v in exp.items()}
        want = {"A": a, "B": b, "C": c, "D": disc}
        ok = all(sums.get(k) == want[k] for k in want)
        checked += 1
        if s3cls[cur] != "UNCERTAIN":
            decided += 1
            if not ok:
                bad = [k for k in want if sums.get(k) != want[k]]
                fails.append((cur, "expansion sums (decided row)", bad, s3cls[cur]))
            if s3cls[cur] != sign_cls:
                fails.append((cur, "s3 class vs disc sign", s3cls[cur], sign_cls))
        else:
            unc_rows.append((cur, fams[cur], "sums-exact" if ok else "sums-inexact"))
        cur = None

from collections import Counter
famcount = Counter(fams[r] for r in cat if s3cls.get(r) != "UNCERTAIN")
print(f"sphere rows checked: {checked}; decided rows requiring exact sums: {decided}")
print(f"decided rows by family: {dict(sorted(famcount.items()))}")
print(f"exact_extra Fraction cross-checks equal: {extra_cross}")
print(f"s3 UNCERTAIN rows (sums reported, not required): {unc_rows}")
print(f"FAILURES: {len(fails)}")
for row in fails[:20]:
    print("  FAIL", row)
sys.exit(1 if fails else 0)
