# monotonicity.py - compare primary vs tolerance-halved host
# runs: tolerance halving must not increase UNCERTAIN torus rays
# and no decided torus ray may flip. Sphere/box lines must be
# identical decisions (tolerance only affects torus).
import sys


def parse(path):
    rays = {}
    for ln in open(path):
        if ln.startswith("RAY "):
            kv = dict(t.split("=", 1) for t in ln.split()[1:])
            rays[int(kv["id"])] = kv
    return rays


a = parse(sys.argv[1])
b = parse(sys.argv[2])
assert set(a) == set(b), "ray id sets differ"
bad = []
unc_a = unc_b = 0
for rid in sorted(a):
    ka, kb = a[rid], b[rid]
    if ka["kind"] == "torus":
        if ka["dec"] == "UNCERTAIN":
            unc_a += 1
        if kb["dec"] == "UNCERTAIN":
            unc_b += 1
        if (ka["dec"] != "UNCERTAIN" and kb["dec"] != "UNCERTAIN"
                and ka["dec"] != kb["dec"]):
            bad.append("torus %d flip %s->%s" % (rid, ka["dec"], kb["dec"]))
        if ka["dec"] != "UNCERTAIN" and kb["dec"] == "UNCERTAIN":
            bad.append("torus %d decided->UNCERTAIN under halving" % rid)
    elif ka["kind"] == "sphere":
        if (ka["s1"], ka["s2"], ka["s3"], ka["final"]) != \
           (kb["s1"], kb["s2"], kb["s3"], kb["final"]):
            bad.append("sphere %d changed under torus halving" % rid)
    elif ka["dec"] != kb["dec"]:
        bad.append("box %d changed under torus halving" % rid)
print("torus UNCERTAIN primary=%d half=%d" % (unc_a, unc_b))
if unc_b > unc_a:
    bad.append("UNCERTAIN increased under halving")
for m in bad:
    print("FAIL:", m)
print("MONOTONICITY", "PASS" if not bad else "FAIL")
sys.exit(1 if bad else 0)
