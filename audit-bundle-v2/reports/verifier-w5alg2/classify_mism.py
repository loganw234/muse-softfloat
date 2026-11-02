#!/usr/bin/env python3
"""classify_mism.py - classify mismatch lines by defect class."""
import sys
from collections import Counter

path = sys.argv[1]
c = Counter()
ex = {}
for line in open(path):
    t = line.split()
    if len(t) < 6:
        continue
    fi, a, b = int(t[0]), int(t[1], 16), int(t[2], 16)
    rm = t[3].split("=")[1]
    k = t[4].split("=")[1]
    m = t[5].split("=")[1]
    kb, kf = k.split("/")
    mb, mf = m.split("/")
    w = 16 if fi == 0 else 32 if fi == 2 - 1 and False else (32 if fi == 1 else 64)
    zero_enc = {0, 1 << (w - 1)}
    if a in zero_enc and b in zero_enc:
        cls = "zero-sign"
    elif kb != mb:
        cls = "bits-diverge"
    else:
        cls = "inexact-dropped"
    c[(fi, cls, rm)] += 1
    ex.setdefault((fi, cls), line.strip())
for k in sorted(c):
    print(k, c[k])
print()
for k in sorted(ex):
    print(k, ex[k])
