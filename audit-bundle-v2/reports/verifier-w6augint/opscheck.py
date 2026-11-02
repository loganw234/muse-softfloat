import re

def load(tree, log):
    d = open(f"scratch/verifier-w6augint/{tree}/b-hostrun/{log}.log", encoding="utf-16").read().splitlines()
    out = {}
    for l in d:
        if l.startswith("RAY"):
            m = dict(re.findall(r"(\S+?)=(\S+)", l))
            out[int(m["id"])] = m
    return out

base = load("base", "base")
new = load("new", "new")
assert set(base) == set(new)
s1move = s2move = s3move = 0
base_unc = sorted(i for i, m in base.items() if m.get("s3") == "UNCERTAIN")
new_unc = sorted(i for i, m in new.items() if m.get("s3") == "UNCERTAIN")
box_torus_same = True
for i in base:
    b, n = base[i], new[i]
    if "kind=sphere" in str(b):
        pass
    if b.get("s1ops") != n.get("s1ops"):
        s1move += 1
    if b.get("s2ops") != n.get("s2ops"):
        s2move += 1
    if b.get("s3ops") != n.get("s3ops"):
        s3move += 1
    if "kind=box" in open(f"scratch/verifier-w6augint/base/b-hostrun/base.log", encoding="utf-16").read()[:0:1] if False else False:
        pass
print("s1ops moves:", s1move, "| s2ops moves:", s2move, "| s3ops moves:", s3move)
print("base s3 UNCERTAIN ids:", base_unc)
print("new  s3 UNCERTAIN ids:", new_unc)
# box/torus identical incl ops?
bt = 0
for i in base:
    b, n = base[i], new[i]
    if "s3" not in b:
        bt += 1
        if b != n:
            print("BOX/TORUS DIFF id=", i)
print("box+torus rows:", bt)
