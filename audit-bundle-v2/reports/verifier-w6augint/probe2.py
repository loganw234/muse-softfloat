from fractions import Fraction
import re

def f64(bits):
    s = (bits >> 63) & 1
    e = (bits >> 52) & 0x7FF
    f = bits & ((1 << 52) - 1)
    if e == 0:
        v = Fraction(f, 1 << 1074)
    elif e == 0x7FF:
        raise ValueError("non-finite input")
    elif e >= 1075:
        v = Fraction(((1 << 52) + f) << (e - 1075), 1)
    else:
        v = Fraction((1 << 52) + f, 1 << (1075 - e))
    return -v if s else v

def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), Fraction(0))

cat = open("scratch/verifier-w6augint/new/tests/interval_catalogue.tsv", encoding="utf-8").read().splitlines()
sph = [l.split("\t") for l in cat if l and not l.startswith("#") and l.split("\t")[2] == "sphere"]
print("sphere rows:", len(sph))

def load(tree, log):
    d = open(f"scratch/verifier-w6augint/{tree}/b-hostrun/{log}.log", encoding="utf-16").read().splitlines()
    out = {}
    for l in d:
        if l.startswith("RAY") and "kind=sphere" in l:
            m = dict(re.findall(r"(\S+?)=(\S+)", l))
            out[int(m["id"])] = m["s3"]
    return out

base = load("base", "base")
new = load("new", "new")

# stated subset: guard rows 682-685 + all tangent400 rows; then full 693
mismatch_extra = 0
mismatch_exact = 0
guard_info = []
tan_rows = 0
res = {}
for r in sph:
    rid = int(r[0])
    fam = r[1]
    O = [f64(int(x, 16)) for x in r[4:7]]
    D = [f64(int(x, 16)) for x in r[7:10]]
    C = [f64(int(x, 16)) for x in r[10:13]]
    rr = f64(int(r[13], 16))
    L = [o - c for o, c in zip(O, C)]
    a = dot(D, D)
    b = dot(L, D)
    c = dot(L, L) - rr * rr
    disc = b * b - a * c
    exp = "HIT" if disc >= 0 else "MISS"
    extra = r[18].strip()
    if Fraction(extra) != disc:
        mismatch_extra += 1
        if len([1]) and mismatch_extra <= 5:
            print("EXTRA-MISMATCH id=", rid, extra, disc)
    if r[16] != exp:
        mismatch_exact += 1
        print("EXACT-COL-MISMATCH id=", rid, r[16], exp)
    res[rid] = exp
    if rid in (682, 683, 684, 685):
        guard_info.append((rid, fam, exp, r[16], extra, base.get(rid), new.get(rid)))
    if fam == "tangent400":
        tan_rows += 1

print("exact_extra mismatches:", mismatch_extra, "| exact-col mismatches:", mismatch_exact)
print("tangent400 sphere rows:", tan_rows)
print("guard rows (id fam py-exact cat-exact base-s3 new-s3):")
for g in guard_info:
    print("  ", g)

for name, run in [("base", base), ("new", new)]:
    dw = sum(1 for rid, e in res.items() if run.get(rid) in ("HIT", "MISS") and run.get(rid) != e)
    unc = sum(1 for rid in res if run.get(rid) == "UNCERTAIN")
    agr = sum(1 for rid, e in res.items() if run.get(rid) == e)
    print(f"{name}: decided-wrong={dw} uncertain={unc} agree={agr} of {len(res)}")
