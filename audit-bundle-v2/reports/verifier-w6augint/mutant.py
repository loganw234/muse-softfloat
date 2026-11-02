import re
from fractions import Fraction

def f64(bits):
    s = (bits >> 63) & 1
    e = (bits >> 52) & 0x7FF
    f = bits & ((1 << 52) - 1)
    if e == 0:
        v = Fraction(f, 1 << 1074)
    elif e == 0x7FF:
        raise ValueError("non-finite")
    elif e >= 1075:
        v = Fraction(((1 << 52) + f) << (e - 1075), 1)
    else:
        v = Fraction((1 << 52) + f, 1 << (1075 - e))
    return -v if s else v

def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), Fraction(0))

cat = open("scratch/verifier-w6augint/new/tests/interval_catalogue.tsv", encoding="utf-8").read().splitlines()
exp = {}
for l in cat:
    if not l or l.startswith("#"):
        continue
    r = l.split("\t")
    if r[2] != "sphere":
        continue
    O = [f64(int(x, 16)) for x in r[4:7]]
    D = [f64(int(x, 16)) for x in r[7:10]]
    C = [f64(int(x, 16)) for x in r[10:13]]
    rr = f64(int(r[13], 16))
    L = [o - c for o, c in zip(O, C)]
    disc = dot(L, D) ** 2 - dot(D, D) * (dot(L, L) - rr * rr)
    exp[int(r[0])] = "HIT" if disc >= 0 else "MISS"

d = open("scratch/verifier-w6augint/new-noguard/b-hostrun/noguard.log", encoding="utf-16").read().splitlines()
run = {}
for l in d:
    if l.startswith("RAY") and "kind=sphere" in l:
        m = dict(re.findall(r"(\S+?)=(\S+)", l))
        run[int(m["id"])] = m["s3"]
print("mutant rows:", len(run))
dw = [(rid, e, run[rid]) for rid, e in exp.items() if run.get(rid) in ("HIT", "MISS") and run[rid] != e]
unc = sum(1 for rid in exp if run.get(rid) == "UNCERTAIN")
print("noguard decided-wrong:", len(dw), "uncertain:", unc)
print("first 12 wrong:", dw[:12])
print("guard rows:", [(rid, exp[rid], run.get(rid)) for rid in (682, 683, 684, 685)])
sm = [l for l in d if l.startswith("SUMMARY") or l.startswith("HOST_SHA256")]
print(sm)
