#!/usr/bin/env python3
# 06_compare.py - compare baseline vs tol-half torus decisions.
B = "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4interval/build/"


def torus(path):
    d = {}
    with open(path) as fh:
        for ln in fh:
            if "kind=torus" in ln:
                t = dict(kv.split("=", 1) for kv in ln.split()[1:])
                d[int(t["id"])] = t
    return d


base, half = torus(B + "host_out.txt"), torus(B + "host_half.txt")
assert set(base) == set(half) and len(base) == 5
unc_b = sum(1 for t in base.values() if t["dec"] == "UNCERTAIN")
unc_h = sum(1 for t in half.values() if t["dec"] == "UNCERTAIN")
print("torus baseline:", {i: base[i]["dec"] for i in sorted(base)})
print("torus half-tol:", {i: half[i]["dec"] for i in sorted(half)})
print("UNCERTAIN baseline/half:", unc_b, unc_h)
flips = [i for i in base
         if base[i]["dec"] != "UNCERTAIN" and half[i]["dec"] != "UNCERTAIN"
         and base[i]["dec"] != half[i]["dec"]]
print("decided flips under halving:", flips)
wider = [i for i in base if half[i]["dec"] == "UNCERTAIN"
         and base[i]["dec"] != "UNCERTAIN"]
print("decided->UNCERTAIN under halving:", wider)

# cap run: every torus row UNCERTAIN with caphit=1
n = u = c = 0
with open(B + "host_cap100.txt") as fh:
    for ln in fh:
        if "kind=torus" in ln:
            n += 1
            t = dict(kv.split("=", 1) for kv in ln.split()[1:])
            u += t["dec"] == "UNCERTAIN"
            c += t["caphit"] == "1"
print("cap100: torus rows / UNCERTAIN / caphit=1:", n, u, c)

# stage monotonicity from baseline sphere rows
s = {}
with open(B + "host_out.txt") as fh:
    for ln in fh:
        if "kind=sphere" in ln:
            t = dict(kv.split("=", 1) for kv in ln.split()[1:])
            s[int(t["id"])] = (t["s1"], t["s2"], t["s3"])
u1 = sum(1 for v in s.values() if v[0] == "UNCERTAIN")
u2 = sum(1 for v in s.values() if v[1] == "UNCERTAIN")
u3 = sum(1 for v in s.values() if v[2] == "UNCERTAIN")
fl = [i for i, v in s.items()
      if len({x for x in v if x != "UNCERTAIN"}) > 1]
print("stage UNCERTAIN s1/s2/s3:", u1, u2, u3, "monotone:", u1 >= u2 >= u3)
print("stage flips:", len(fl), fl[:10])

# survey sanity: tangent400 staging + limb band + torus march-miss
import struct


def f64(b):
    return struct.unpack(">d", struct.pack(">Q", int(b, 16)))[0]


cat = {}
with open("C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-interval/tests/interval_catalogue.tsv") as fh:
    for ln in fh:
        if ln.startswith("#") or not ln.strip():
            continue
        p = ln.rstrip("\n").split("\t")
        cat[int(p[0])] = (p[1], p[2], p[16], p[17])
tan = [i for i, v in cat.items() if v[0] == "tangent400"]
d1 = sum(1 for i in tan if s[i][0] != "UNCERTAIN")
d2 = sum(1 for i in tan if s[i][1] != "UNCERTAIN")
d3 = sum(1 for i in tan if s[i][2] != "UNCERTAIN")
print("tangent400 staging decided s1/s2/s3:", d1, d2, d3, "n=", len(tan))
limb_ids = sorted(i for i, v in cat.items() if v[0] == "limb")
band = sum(1 for i in limb_ids if s[i][0] == "UNCERTAIN")
print("limb: n=%d s1-UNCERTAIN-band=%d" % (len(limb_ids), band))
print("limb naive-vs-exact disagreements:",
      sum(1 for i in limb_ids if cat[i][3] != cat[i][2] and cat[i][3] != "TANGENT0"))
print("torus rows exact/naive:",
      [(i, cat[i][2], cat[i][3]) for i in cat if cat[i][1] == "torus"])
