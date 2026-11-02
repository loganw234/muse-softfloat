import re
from collections import Counter

def load(tree, log):
    d = open(f"scratch/verifier-w6augint/{tree}/b-hostrun/{log}.log", encoding="utf-16").read().splitlines()
    out = {}
    for l in d:
        if l.startswith("RAY") and "kind=sphere" in l:
            m = dict(re.findall(r"(\S+?)=(\S+)", l))
            out[int(m["id"])] = (m["fam"], m["s3"], m["final"], m.get("s3ops"))
    return out

base = load("base", "base")
new = load("new", "new")
flips = Counter()
fam = Counter()
for rid in base:
    if base[rid][1] != new[rid][1]:
        flips[(base[rid][1], new[rid][1])] += 1
        fam[new[rid][0]] += 1
print("s3 flip directions (base->new):", dict(flips))
print("mismatched rows by family:", dict(fam))
# guard rows detail
for rid in (682, 683, 684, 685):
    print(rid, base[rid], new[rid])
