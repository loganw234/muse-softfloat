#!/usr/bin/env python3
"""census_teta.py - per-format file te!=ta pair counts + ties examples."""
import sys

for f in (16, 32, 64):
    seen = {}
    sub = 0
    t_ = 10 if f == 16 else 23 if f == 32 else 52
    w = f
    ew = w - 1 - t_
    for line in open(f"worktrees/verify5-alg2/tests/vectors/alg-f{f}.vec"):
        t = line.split()
        if len(t) >= 8 and "hypot" in t[0]:
            seen.setdefault((t[2], t[3]), {})[t[1]] = (t[5], t[6])
            ef = (int(t[5], 16) >> t_) & ((1 << ew) - 1)
            if ef == 0 and (int(t[5], 16) & ((1 << t_) - 1)) != 0:
                sub += 1
    n = sum(1 for m in seen.values() if m.get("te") != m.get("ta"))
    print(f"f{f}: pairs={len(seen)} te!=ta={n} subnormal-lines={sub}")
    # show two te!=ta examples
    shown = 0
    for (a, b), m in seen.items():
        if m.get("te") != m.get("ta") and shown < 2:
            print(f"  ex a={a} b={b} te={m.get('te')} ta={m.get('ta')}")
            shown += 1
