#!/usr/bin/env python3
# 04_row2.py - inspect TSV row id=2 vs independent exact recomputation.
import struct
from fractions import Fraction

TSV = "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-interval/tests/interval_catalogue.tsv"


def f64(bits):
    return struct.unpack(">d", struct.pack(">Q", int(bits, 16)))[0]


with open(TSV) as fh:
    for ln in fh:
        if ln.startswith("#") or not ln.strip():
            continue
        p = ln.rstrip("\n").split("\t")
        if int(p[0]) != 2:
            continue
        O = [f64(x) for x in p[4:7]]
        D = [f64(x) for x in p[7:10]]
        g = [f64(x) for x in p[10:16]]
        print("fam:", p[1], "kind:", p[2])
        print("prov:", p[3])
        print("O:", O)
        print("D:", D)
        print("C:", g[:3], "r:", g[3])
        print("TSV exact:", p[16], "naive:", p[17], "extra:", p[18])
        OF = [Fraction(v) for v in O]
        DF = [Fraction(v) for v in D]
        CF = [Fraction(v) for v in g[:3]]
        rF = Fraction(g[3])
        L = [OF[i] - CF[i] for i in range(3)]
        a = sum(DF[i] * DF[i] for i in range(3))
        b = sum(L[i] * DF[i] for i in range(3))
        c = sum(L[i] * L[i] for i in range(3)) - rF * rF
        print("a =", a, "\nb =", b, "\nc =", c)
        print("b^2-a*c =", b * b - a * c)
        print("b^2+a*c =", b * b + a * c)
