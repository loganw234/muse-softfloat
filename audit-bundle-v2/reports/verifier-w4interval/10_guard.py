#!/usr/bin/env python3
# 10_guard.py - inspect guard rows 682/683 under the P1 (correct-RD) build.
import struct
from fractions import Fraction

B = "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4interval/mut/p1.txt"
T = "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-interval/tests/interval_catalogue.tsv"


def f64(b):
    return struct.unpack(">d", struct.pack(">Q", int(b, 16)))[0]


for ln in open(B):
    if ln.startswith("RAY id=68"):
        print(ln.strip())
for ln in open(T):
    if ln.startswith("#") or not ln.strip():
        continue
    p = ln.rstrip("\n").split("\t")
    if int(p[0]) in (682, 683):
        O = [Fraction(f64(x)) for x in p[4:7]]
        D = [Fraction(f64(x)) for x in p[7:10]]
        C = [Fraction(f64(p[10 + i])) for i in range(3)]
        r = Fraction(f64(p[13]))
        L = [O[i] - C[i] for i in range(3)]
        a = sum(D[i] * D[i] for i in range(3))
        b = sum(L[i] * D[i] for i in range(3))
        c = sum(L[i] * L[i] for i in range(3)) - r * r
        ex = b * b - a * c
        print("id", p[0], "exact disc = %.6e" % float(ex), "num bits:", ex.numerator.bit_length())
        print("   prov:", p[3], "TSV exact:", p[16])
