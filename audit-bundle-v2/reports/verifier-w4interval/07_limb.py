#!/usr/bin/env python3
# 07_limb.py - limb scanline microstructure (recomputed, not quoted).
B = "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4interval/build/"
T = "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-interval/tests/interval_catalogue.tsv"

cat = {}
with open(T) as fh:
    for ln in fh:
        if ln.startswith("#") or not ln.strip():
            continue
        p = ln.rstrip("\n").split("\t")
        if p[1] == "limb":
            cat[int(p[0])] = (p[3], p[16], p[17])
host = {}
with open(B + "host_out.txt") as fh:
    for ln in fh:
        if "kind=sphere" in ln:
            t = dict(kv.split("=", 1) for kv in ln.split()[1:])
            host[int(t["id"])] = (t["s1"], t["s2"], t["s3"], t["final"])
ids = sorted(cat)
print("limb n =", len(ids))
from collections import Counter
print("exact:", Counter(v[1] for v in cat.values()))
print("naive:", Counter(v[2] for v in cat.values()))
print("naive!=exact (incl TANGENT0):",
      sum(1 for v in cat.values() if v[2] != v[1]))
print("naive sign-wrong (HIT/MISS flipped):",
      sum(1 for v in cat.values() if v[2] != v[1] and v[2] != "TANGENT0"))
print("naive TANGENT0:", sum(1 for v in cat.values() if v[2] == "TANGENT0"))
# longest consecutive s1-UNCERTAIN run in catalogue order
run = best = 0
for i in ids:
    run = run + 1 if host[i][0] == "UNCERTAIN" else 0
    best = max(best, run)
print("s1 UNCERTAIN total:", sum(1 for i in ids if host[i][0] == "UNCERTAIN"),
      "longest run:", best)
run = best = 0
for i in ids:
    run = run + 1 if host[i][3] == "UNCERTAIN" else 0
    best = max(best, run)
print("final UNCERTAIN total:", sum(1 for i in ids if host[i][3] == "UNCERTAIN"),
      "longest run:", best)
# where does exact cross zero?
ex = [1 if cat[i][1] == "HIT" else -1 for i in ids]
for k in range(len(ex) - 1):
    if ex[k] != ex[k + 1]:
        print("exact crossing between step", k, "ids", ids[k], ids[k + 1])
# first naive MISS index vs exact
nv = [1 if cat[i][2] == "HIT" else (-1 if cat[i][2] == "MISS" else 0) for i in ids]
print("first naive MISS step:", next((k for k, v in enumerate(nv) if v == -1), None))
print("first exact MISS step:", next((k for k, v in enumerate(ex) if v == -1), None))
