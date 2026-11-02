#!/usr/bin/env python3
# 14_stage.py - per-family staging under baseline vs P1 (correct RD).
import sys

B = "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4interval/"
T = "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-interval/tests/interval_catalogue.tsv"

fam = {}
with open(T) as fh:
    for ln in fh:
        if ln.startswith("#") or not ln.strip():
            continue
        p = ln.rstrip("\n").split("\t")
        fam[int(p[0])] = p[1]


def load(path):
    s = {}
    with open(path) as fh:
        for ln in fh:
            if "kind=sphere" in ln:
                t = dict(kv.split("=", 1) for kv in ln.split()[1:])
                s[int(t["id"])] = (t["s1"], t["s2"], t["s3"])
    return s


for tag, path in (("baseline", B + "build/host_out.txt"),
                  ("P1-correct-RD", B + "mut/p1.txt")):
    s = load(path)
    print("===", tag)
    for f in ("tangent400", "limb", "adv2k", "guard", "ordinary"):
        ids = [i for i, v in fam.items() if v == f]
        d1 = sum(1 for i in ids if s[i][0] != "UNCERTAIN")
        d2 = sum(1 for i in ids if s[i][1] != "UNCERTAIN")
        d3 = sum(1 for i in ids if s[i][2] != "UNCERTAIN")
        print("  %-10s n=%3d decided s1/s2/s3=%d/%d/%d" % (f, len(ids), d1, d2, d3))
    limb = sorted(i for i, v in fam.items() if v == "limb")
    run = best = 0
    for i in limb:
        run = run + 1 if s[i][0] == "UNCERTAIN" else 0
        best = max(best, run)
    print("  limb s1-UNCERTAIN longest consecutive run:", best)
